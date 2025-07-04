#!/usr/bin/env python
import argparse
import logging
import os

import pandas as pd
import wandb


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="process_data")

    logger.info("Downloading artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()

    df = pd.read_parquet(artifact_path)

    # Drop the duplicates
    logger.info("Dropping duplicates")
    df = df.drop_duplicates().reset_index(drop=True)

    # Fill NaNs in 'title' and 'song_name' before creating text_feature
    logger.info("Filling missing values in title and song_name")
    df['title'].fillna('', inplace=True)
    df['song_name'].fillna('', inplace=True)

    # Create 'text_feature'
    logger.info("Creating text feature")
    df['text_feature'] = df['title'] + ' ' + df['song_name']

    # Drop rows with NaNs in critical numeric columns (like loudness)
    logger.info("Dropping rows with missing values in important columns")
    required_columns = [
        'danceability', 'energy', 'loudness', 'speechiness',
        'acousticness', 'instrumentalness', 'liveness',
        'valence', 'tempo', 'duration_ms', 'key', 'time_signature', 'genre'
    ]
    df.dropna(subset=required_columns, inplace=True)


    filename = "processed_data.csv"
    df.to_csv(filename)

    artifact = wandb.Artifact(
        name=args.artifact_name,
        type=args.artifact_type,
        description=args.artifact_description,
    )
    artifact.add_file(filename)

    logger.info("Logging artifact")
    run.log_artifact(artifact)

    os.remove(filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Preprocess a dataset",
        fromfile_prefix_chars="@",
    )

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Fully-qualified name for the input artifact",
        required=True,
    )

    parser.add_argument(
        "--artifact_name", type=str, help="Name for the artifact", required=True
    )

    parser.add_argument(
        "--artifact_type", type=str, help="Type for the artifact", required=True
    )

    parser.add_argument(
        "--artifact_description",
        type=str,
        help="Description for the artifact",
        required=True,
    )

    args = parser.parse_args()

    go(args)
