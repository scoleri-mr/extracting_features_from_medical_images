import torch
import numpy as np


def extract_latent_vectors(model, dataloader, device):
    latent_vectors = []
    labels = []
    model.eval()
    with torch.no_grad():
        for data, target, _, _ in dataloader:
            data = data.to(device)
            target = target.to(device)
            mu, logvar = model.encode(data)
            latent_vector = model.reparameterize(mu, logvar)
            latent_vectors.append(latent_vector.cpu().numpy())
            labels.append(target.cpu().numpy())
    return np.concatenate(latent_vectors), np.concatenate(labels)


def extract_latents(model, dataloader, device, result_path):
    latent_vectors, labels = extract_latent_vectors(model, dataloader, device)

    np.save(f"{result_path}_latents.npy", latent_vectors)
    np.save(f"{result_path}_labels.npy", labels)

    return (latent_vectors, labels)
