import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import os

from vectorizer import RGBVectorCanvas, get_device

def train_turbo_hybrid(image_path, epochs=40):
    device = get_device()
    img = Image.open(image_path).convert('RGB').resize((128, 128))
    transform = transforms.ToTensor()
    target_img = transform(img).to(device)
    
    # Modelo para Adam Puro
    model_adam = RGBVectorCanvas(num_strokes=150, canvas_size=128, device=device).to(device)
    opt_adam = optim.Adam(model_adam.parameters(), lr=0.1)
    
    # Modelo para el Turbo Híbrido
    model_turbo = RGBVectorCanvas(num_strokes=150, canvas_size=128, device=device).to(device)
    model_turbo.load_state_dict(model_adam.state_dict())
    opt_turbo_refine = optim.Adam(model_turbo.parameters(), lr=0.1)
    
    # Hiperparámetros del Turbo
    LR_MULT_ALPHAS = 120.0
    LR_MULT_POINTS = 0.5  # Las coordenadas son más sensibles, bajamos un poco
    SWITCH_EPOCH = 7      # Cuándo pasar de Multiplicativo a Adam
    
    history_adam = []
    history_turbo = []
    
    print(f"Iniciando Duelo Final: Adam vs Turbo-Híbrido (Switch en época {SWITCH_EPOCH})")
    print(f"{'Epoch':<6} | {'Adam Loss':<12} | {'Turbo Loss':<12} | {'Mode':<10}")
    print("-" * 50)
    
    for epoch in range(1, epochs + 1):
        # 1. Update Adam Estándar
        opt_adam.zero_grad()
        l_adam = nn.functional.mse_loss(model_adam(), target_img)
        l_adam.backward()
        opt_adam.step()
        history_adam.append(l_adam.item())
        
        # 2. Update Turbo
        opt_turbo_refine.zero_grad()
        l_turbo = nn.functional.mse_loss(model_turbo(), target_img)
        l_turbo.backward()
        
        mode = "TURBO"
        if epoch <= SWITCH_EPOCH:
            # FASE 1: MULTIPLICATIVO PURO EN TODO
            with torch.no_grad():
                # Update Multiplicativo en todos los parámetros
                for name, p in model_turbo.named_parameters():
                    if p.grad is not None:
                        # Usamos diferentes velocidades según el tipo de parámetro
                        lr = LR_MULT_ALPHAS if "alpha" in name or "sigma" in name else LR_MULT_POINTS
                        p.data *= torch.exp(-lr * p.grad)
        else:
            # FASE 2: CAMBIO DE MARCHAS A ADAM
            mode = "ADAM-REFINE"
            opt_turbo_refine.step()
            
        history_turbo.append(l_turbo.item())
        print(f"{epoch:<6} | {l_adam.item():<12.5f} | {l_turbo.item():<12.5f} | {mode:<10}")

    # Gráfica
    plt.figure(figsize=(10, 5))
    plt.plot(history_adam, label="Adam Puro", color='blue')
    plt.plot(history_turbo, label="Turbo Híbrido (Mult -> Adam)", color='red', linewidth=2)
    plt.axvline(x=SWITCH_EPOCH, color='gray', linestyle='--', label="Switch Point")
    plt.title("Efecto del Optimizador Multiplicativo Inicial")
    plt.xlabel("Época")
    plt.ylabel("MSE Loss")
    plt.yscale('log')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    os.makedirs("results/tests", exist_ok=True)
    plt.savefig("results/tests/turbo_final_comparison.png")
    
    # Guardar previews
    plt.imsave("results/tests/preview_adam.png", model_adam().detach().cpu().permute(1, 2, 0).numpy())
    plt.imsave("results/tests/preview_turbo.png", model_turbo().detach().cpu().permute(1, 2, 0).numpy())
    
    print(f"\n¡Prueba terminada! Mira la gráfica en results/tests/turbo_final_comparison.png")
    if history_turbo[-1] < history_adam[-1]:
        mejoría = (history_adam[-1] - history_turbo[-1]) / history_adam[-1] * 100
        print(f"El Turbo Híbrido ha ganado por un {mejoría:.2f}% de precisión extra.")
    else:
        print("Adam ha recuperado terreno al final, pero mira el inicio de la curva.")

if __name__ == "__main__":
    test_image = "results/final_raster.png"
    if os.path.exists(test_image):
        train_turbo_hybrid(test_image)
    else:
        print("No se encontró imagen para el test.")
