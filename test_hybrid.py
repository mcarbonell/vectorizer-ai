import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import os

from vectorizer import RGBVectorCanvas, get_device

def train_hybrid_comparison(image_path, epochs=40):
    device = get_device()
    # Cargamos imagen pequeña para velocidad máxima
    img = Image.open(image_path).convert('RGB').resize((64, 64))
    transform = transforms.ToTensor()
    target_img = transform(img).to(device)
    
    # --- MODELO A: ADAM SOLO ---
    model_adam = RGBVectorCanvas(num_strokes=100, canvas_size=64, device=device).to(device)
    optimizer_adam = optim.Adam(model_adam.parameters(), lr=0.1)
    
    # --- MODELO B: ADAM + MULTIPLICADOR (HÍBRIDO) ---
    model_hybrid = RGBVectorCanvas(num_strokes=100, canvas_size=64, device=device).to(device)
    model_hybrid.load_state_dict(model_adam.state_dict()) # Empezamos del mismo punto exacto
    optimizer_hybrid = optim.Adam(model_hybrid.parameters(), lr=0.1)
    
    lr_mult = 0.02 # El "empujón" multiplicativo

    history_adam = []
    history_hybrid = []
    
    print(f"Iniciando Sprint de {epochs} épocas...")
    print(f"{'Epoch':<6} | {'Adam Loss':<12} | {'Hybrid Loss':<12}")
    print("-" * 35)
    
    for epoch in range(1, epochs + 1):
        # --- 1. Train Adam Solo ---
        optimizer_adam.zero_grad()
        loss_adam = nn.functional.mse_loss(model_adam(), target_img)
        loss_adam.backward()
        optimizer_adam.step()
        history_adam.append(loss_adam.item())
        
        # --- 2. Train Hybrid (Adam + Mult) ---
        optimizer_hybrid.zero_grad()
        loss_hybrid = nn.functional.mse_loss(model_hybrid(), target_img)
        loss_hybrid.backward()
        
        # Primero el paso de Adam estándar
        optimizer_hybrid.step()
        
        # Segundo: El "Empujón Multiplicativo" sobre Alpha y Sigma
        with torch.no_grad():
            # Solo aplicamos el multiplicador si hay gradiente
            if model_hybrid.alpha_logit.grad is not None:
                model_hybrid.alpha_logit.data *= torch.exp(-lr_mult * model_hybrid.alpha_logit.grad)
            if model_hybrid.log_sigma.grad is not None:
                model_hybrid.log_sigma.data *= torch.exp(-lr_mult * model_hybrid.log_sigma.grad)
        
        history_hybrid.append(loss_hybrid.item())
        
        print(f"{epoch:<6} | {loss_adam.item():<12.5f} | {loss_hybrid.item():<12.5f}")

    # Gráfica de resultados
    plt.figure(figsize=(8, 4))
    plt.plot(history_adam, label="Adam Estándar", color='blue')
    plt.plot(history_hybrid, label="Adam + Multiplicador (Híbrido)", color='red', linestyle='--')
    plt.title("Comparación de Convergencia Rápida (40 épocas)")
    plt.xlabel("Época")
    plt.ylabel("MSE Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    os.makedirs("results/tests", exist_ok=True)
    plt.savefig("results/tests/hybrid_comparison.png")
    print("\nGráfica guardada en results/tests/hybrid_comparison.png")
    
    # Ver si uno ha bajado más que otro al final
    diff = (history_adam[-1] - history_hybrid[-1]) / history_adam[-1] * 100
    if diff > 0:
        print(f"¡ÉXITO! El Híbrido es un {diff:.2f}% más eficiente en 40 épocas.")
    else:
        print(f"Adam estándar sigue ganando por un {-diff:.2f}%.")

if __name__ == "__main__":
    test_image = "results/final_raster.png"
    if os.path.exists(test_image):
        train_hybrid_comparison(test_image)
    else:
        print("Error: No hay imagen para testear. Ejecuta vectorizer.py primero.")
