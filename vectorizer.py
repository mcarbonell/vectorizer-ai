import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
import matplotlib.pyplot as plt
import os
import numpy as np
from PIL import Image
import argparse

def get_device():
    """Checks for available devices: DirectML (AMD), CUDA (NVIDIA), or CPU."""
    try:
        import torch_directml
        device = torch_directml.device()
        return device
    except ImportError:
        if torch.cuda.is_available():
            return torch.device("cuda")
        else:
            return torch.device("cpu")

class RGBVectorCanvas(nn.Module):
    """
    Differentiable RGB Painter with variable stroke thickness.
    """
    def __init__(self, num_strokes=100, canvas_size=128, device='cpu'):
        super().__init__()
        self.num_strokes = num_strokes
        self.canvas_size = canvas_size
        
        # 3 points per stroke (x, y)
        self.points = nn.Parameter(torch.rand(num_strokes, 3, 2) * canvas_size)
        
        # Colors (RGB) - logits
        self.colors_logit = nn.Parameter(torch.randn(num_strokes, 3))
        
        # Opacity (Alpha)
        self.alpha_logit = nn.Parameter(torch.randn(num_strokes, 1))
        
        # Stroke thickness (Sigma) - optimized per stroke
        # We use log scale to keep it positive: sigma = exp(log_sigma)
        self.log_sigma = nn.Parameter(torch.full((num_strokes, 1), 0.5)) # start with sigma ~1.6
        
        # Grid for rendering
        y, x = torch.meshgrid(
            torch.linspace(0, canvas_size-1, canvas_size), 
            torch.linspace(0, canvas_size-1, canvas_size), 
            indexing='ij'
        )
        self.register_buffer("grid", torch.stack([x, y], dim=-1).view(1, canvas_size * canvas_size, 2).to(device))

    def forward(self):
        t = torch.linspace(0, 1, 15, device=self.points.device).view(1, 15, 1)
        p0, p1, p2 = self.points[:, 0:1, :], self.points[:, 1:2, :], self.points[:, 2:3, :]
        
        # Quadratic Bezier
        bezier_points = (1-t)**2 * p0 + 2*(1-t)*t * p1 + t**2 * p2 
        
        # Rendering
        diff = self.grid.unsqueeze(0) - bezier_points.unsqueeze(2) 
        dist_sq = torch.sum(diff**2, dim=-1) 
        min_dist_sq, _ = torch.min(dist_sq, dim=1) 
        
        # Use per-stroke sigma
        sigma = torch.exp(self.log_sigma).view(self.num_strokes, 1)
        masks = torch.exp(-min_dist_sq / (2 * sigma**2)).view(self.num_strokes, self.canvas_size, self.canvas_size)
        
        colors = torch.sigmoid(self.colors_logit) 
        alphas = torch.sigmoid(self.alpha_logit).view(self.num_strokes, 1, 1) 
        
        canvas = torch.ones(3, self.canvas_size, self.canvas_size, device=self.points.device)
        for i in range(self.num_strokes):
            blend = masks[i:i+1, :, :] * alphas[i]
            canvas = canvas * (1 - blend) + colors[i].view(3, 1, 1) * blend
            
        return canvas

def save_svg(model, file_path, width, height):
    """Exports to SVG using filters to mimic Gaussian softness."""
    points = model.points.detach().cpu().numpy()
    colors = torch.sigmoid(model.colors_logit).detach().cpu().numpy()
    alphas = torch.sigmoid(model.alpha_logit).detach().cpu().numpy()
    sigmas = torch.exp(model.log_sigma).detach().cpu().numpy()
    
    scale_x = width / model.canvas_size
    scale_y = height / model.canvas_size
    
    with open(file_path, "w") as f:
        f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n')
        f.write('  <defs>\n')
        # We create a filter to mimic the Gaussian falloff
        f.write('    <filter id="softBlur" x="-50%" y="-50%" width="200%" height="200%">\n')
        f.write('      <feGaussianBlur in="SourceGraphic" stdDeviation="1" />\n')
        f.write('    </filter>\n')
        f.write('  </defs>\n')
        f.write(f'  <rect width="100%" height="100%" fill="white"/>\n')
        
        for i in range(model.num_strokes):
            p = points[i]
            c = (colors[i] * 255).astype(int)
            a = alphas[i][0]
            s = sigmas[i][0]
            
            path_data = (f"M {p[0,0]*scale_x},{p[0,1]*scale_y} "
                         f"Q {p[1,0]*scale_x},{p[1,1]*scale_y} "
                         f"{p[2,0]*scale_x},{p[2,1]*scale_y}")
            
            color_str = f"rgb({c[0]},{c[1]},{c[2]})"
            # stroke-width is approx 4 * sigma to cover the Gaussian area
            # We apply the filter only if sigma is significant
            filter_attr = 'filter="url(#softBlur)"' if s > 0.5 else ''
            
            f.write(f'  <path d="{path_data}" fill="none" stroke="{color_str}" '
                    f'stroke-width="{s * 3.5 * scale_x}" stroke-opacity="{a}" '
                    f'stroke-linecap="round" {filter_attr} />\n')
            
        f.write('</svg>')

def train_image(image_path, num_strokes=200, epochs=1000, lr=0.1, work_res=128):
    device = get_device()
    print(f"Using device: {device}")
    
    img = Image.open(image_path).convert('RGB')
    original_width, original_height = img.size
    
    transform = transforms.Compose([
        transforms.Resize((work_res, work_res)),
        transforms.ToTensor()
    ])
    target_img = transform(img).to(device)
    
    model = RGBVectorCanvas(num_strokes=num_strokes, canvas_size=work_res, device=device).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    print(f"Vectorizing '{image_path}' with {num_strokes} strokes (variable thickness)...")
    for epoch in range(1, epochs + 1):
        optimizer.zero_grad()
        generated_img = model()
        
        loss_recon = nn.functional.mse_loss(generated_img, target_img)
        # Regularization: penalty for too many opacities and too much thickness
        loss_sparse = 0.002 * torch.mean(torch.sigmoid(model.alpha_logit))
        
        loss = loss_recon + loss_sparse
        loss.backward()
        optimizer.step()
        
        if epoch % 100 == 0 or epoch == 1:
            print(f"Epoch {epoch:4d} | Loss: {loss.item():.4f}")

    os.makedirs("results", exist_ok=True)
    final_img = model().detach().cpu().permute(1, 2, 0).numpy()
    plt.imsave("results/final_raster.png", final_img)
    save_svg(model, "results/output.svg", original_width, original_height)
    print(f"Done! Results in 'results/'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vectorizer AI: Image to SVG")
    parser.add_argument("--image", type=str, help="Path to the input image")
    parser.add_argument("--strokes", type=int, default=200, help="Number of strokes")
    parser.add_argument("--epochs", type=int, default=1000, help="Number of epochs")
    parser.add_argument("--res", type=int, default=128, help="Internal resolution")
    
    args = parser.parse_args()
    if args.image:
        train_image(args.image, num_strokes=args.strokes, epochs=args.epochs, work_res=args.res)
    else:
        print("Usage: python vectorizer.py --image path/to/image.jpg")
