import argparse
import numpy as np
from finetune import fine_tune
from extractor import extract_features
import classifier.svm as svm
from utils.plotting import *
from dataset.PatchedDataset import PatchedDataset, train_test_split_loaders
from model.PathDino import get_pathDino_model


def main(args):

    pathdino, dino_transform = get_pathDino_model(
        weights_path=args.pretrained_dino_path
    )

    pathdino.cuda()

    dataset = PatchedDataset(
        root_dir=args.root_dir, num_images=args.num_images, transform=dino_transform
    )

    train_loader, test_loader = train_test_split_loaders(
        dataset, args.batch_size, train_ratio=0.8
    )

    if args.fine_tune:
        print(f"Finetuning pathdino512 from {args.pretrained_dino_path}")
        pathdino = fine_tune(pathdino, train_loader, args.fine_tune_epochs)

    train_features, train_labels = extract_features(train_loader, pathdino)
    test_features, test_labels = extract_features(test_loader, pathdino)

    svm.classify_with_provided_splits(
        train_features,
        train_labels,
        test_features,
        test_labels,
        args.results_path,
        with_pca=True,
        pca_components=args.latent_dim,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PathDino")
    parser.add_argument(
        "--root_dir",
        type=str,
        required=True,
        help="Path to directory containing the patches folders",
    )
    parser.add_argument(
        "--num_images",
        type=int,
        default=24,
        help="How may images to use (test purpose)",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=16,
    )
    parser.add_argument(
        "--latent_dim",
        type=int,
        default=128,
        help="Extracted latent vector dimension, defaults to 128",
    )
    parser.add_argument(
        "--fine_tune_epochs",
        type=int,
        default=10,
        help="Whether to finetune the pretrained dino and number of epochs",
    )
    parser.add_argument(
        "--results_path",
        type=str,
        default="./results/pathdino/",
        help="Name of the experiment, save results in this path.",
    )
    parser.add_argument(
        "--pretrained_dino_path",
        type=str,
        default="./extractors/pathdino/model/PathDino512.pth",
        help="PathDino pretrained weights path",
    )
    args = parser.parse_args()
    args.fine_tune = True if args.fine_tune_epochs > 0 else False

    if args.fine_tune:
        args.results_path = f"{args.results_path}/finetune/pathdino_finetuned_{args.fine_tune_epochs}_bs{args.batch_size}_numimages{args.num_images}_latent{args.latent_dim}"
    else:
        args.results_path = f"{args.results_path}/pathdino_bs{args.batch_size}_numimages{args.num_images}_latent{args.latent_dim}"
    print(args)
    main(args)
