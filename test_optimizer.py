import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import time
import os

# Importamos la lógica del modelo de nuestro archivo original
from vectorizer import RGBVectorCanvas, get_device

def train_comparison(image_path, epochs=40):
    device = get_device()
    img = Image.open(image_path).convert('RGB').resize((128, 128))
    transform = transforms.ToTensor()
    target_img = transform(img).to(device)
    
    # --- MODELO 1: ADAM ESTÁNDAR ---
    model_adam = RGBVectorCanvas(num_strokes=150, canvas_size=128, device=device).to(device)
    optimizer_adam = optim.Adam(model_adam.parameters(), lr=0.1)
    
    # --- MODELO 2: EXPERIMENTAL (Multiplicativo) ---
    model_mult = RGBVectorCanvas(num_strokes=150, canvas_size=128, device=device).to(device)
    # Inicializamos igual
    model_mult.load_state_dict(model_adam.state_dict())
    
    # Para el multiplicativo, usaremos Adam para los puntos (posiciones)
    # Pero haremos un update manual multiplicativo para Alpha y Sigma
    optimizer_mult_base = optim.Adam([model_mult.points, model_mult.colors_logit], lr=0.1)
    lr_mult = 125 # Learning rate para el update multiplicativo

    history_adam = []
    history_mult = []
    
    print(f"Comparando convergencia ({epochs} épocas)...")
    
    start_time = time.time()
    for epoch in range(1, epochs + 1):
        # Update Adam
        optimizer_adam.zero_grad()
        loss_adam = nn.functional.mse_loss(model_adam(), target_img)
        loss_adam.backward()
        optimizer_adam.step()
        history_adam.append(loss_adam.item())
        
        # Update Multiplicativo
        optimizer_mult_base.zero_grad()
        if model_mult.alpha_logit.grad is not None:
            model_mult.alpha_logit.grad.zero_()
        if model_mult.log_sigma.grad is not None:
            model_mult.log_sigma.grad.zero_()
            
        gen_mult = model_mult()
        loss_mult = nn.functional.mse_loss(gen_mult, target_img)
        loss_mult.backward()
        
        # 1. Update estándar para puntos y colores
        optimizer_mult_base.step()
        
        # 2. Update MULTIPLICATIVO para Alpha y Sigma
        with torch.no_grad():
            # w = w * exp(-lr * grad)
            # Esto es equivalente a un update aditivo en el espacio logarítmico
            # pero lo aplicamos directamente para ver el efecto
            model_mult.alpha_logit.data *= torch.exp(-lr_mult * model_mult.alpha_logit.grad)
            model_mult.log_sigma.data *= torch.exp(-lr_mult * model_mult.log_sigma.grad)
            
        history_mult.append(loss_mult.item())
        
        if epoch % 1 == 0:
            print(f"Epoch {epoch:3d} | Adam Loss: {loss_adam.item():.4f} | Mult Loss: {loss_mult.item():.4f}")

    print(f"Tiempo total: {time.time() - start_time:.2f}s")
    
    # --- VISUALIZACIÓN ---
    plt.figure(figsize=(10, 5))
    plt.plot(history_adam, label="Adam (Aditivo)")
    plt.plot(history_mult, label="Experimental (Multiplicativo en Alpha/Sigma)", linestyle='--')
    plt.yscale('log')
    plt.title("Convergencia: Aditivo vs Multiplicativo")
    plt.xlabel("Época")
    plt.ylabel("Loss (MSE)")
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.5)
    
    os.makedirs("results/tests", exist_ok=True)
    plt.savefig("results/tests/optimizer_comparison.png")
    
    # Guardar imágenes finales para comparar "ojo"
    plt.imsave("results/tests/final_adam.png", model_adam().detach().cpu().permute(1, 2, 0).numpy())
    plt.imsave("results/tests/final_mult.png", model_mult().detach().cpu().permute(1, 2, 0).numpy())
    
    print("Gráfica guardada en results/tests/optimizer_comparison.png")

if __name__ == "__main__":
    # Usaremos una de las imágenes que se hayan generado o una por defecto
    # Si no hay imagen, este script fallará, así que asegúrate de tener una.
    test_image = "results/final_raster.png" 
    if os.path.exists(test_image):
        train_comparison(test_image)
    else:
        print(f"No se encontró {test_image}. Ejecuta primero 'python vectorizer.py --image ...'")
