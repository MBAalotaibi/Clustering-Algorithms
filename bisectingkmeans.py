# -*- coding: utf-8 -*-
"""BisectingKMeans

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13wWzpJidRP8ug6ZYFHvbCGw3py-VqXot
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
import os

# Set a fixed seed for numpy's random number generator for reproducibility
np.random.seed(42)


# Function to check if a string can be converted to a float
def is_float(element):
    try:
        float(element)
        return True
    except ValueError:
        return False

# Function to load a dataset from a specified file
def load_dataset(dataset):
    # Check if the file exists
    if not os.path.isfile(dataset):
        raise FileNotFoundError(f"The file {dataset} does not exist.")
    data = []
    # Read the dataset file
    with open(dataset, 'r') as file:
        for line in file:
            parts = line.strip().split()
            # Filter out non-numeric values and convert the rest to float
            numeric_values = [float(part) for part in parts if is_float(part)]
            if numeric_values:  # ensuring there's at least one number in the line
                data.append(numeric_values)

     # Check if any numeric data was loaded
    if not data:
        raise ValueError("No numeric data found in the file.")
    return np.array(data)

# Function to compute the Euclidean distance between two points
def ComputeDistance(point1, point2):
    return np.linalg.norm(point1 - point2)

# Function to randomly select initial centroids from the data
def initialSelection(data, k):
    indices = np.random.choice(len(data), k, replace=False)
    return data[indices]

# Function to assign each data point to the nearest centroid
def assignClusterIds(data, centroids):
    # Calculate the Euclidean distance between every point and each centroid
    distances = np.sqrt(((data - centroids[:, np.newaxis])**2).sum(axis=2))
     # Return the index of the centroid with the minimum distance for each point
    return np.argmin(distances, axis=0)


# Function to compute the mean of points in each cluster as new centroids
def computeClusterRepresentatives(data, labels, k):
    return np.array([data[labels == i].mean(axis=0) for i in range(k)])


# Function to compute the sum of squared distances of all points in a cluster from the cluster mean
def computeSumOfSquares(cluster):
    center = cluster.mean(axis=0)
    return np.sum((cluster - center) ** 2)


# Function implementing the bisecting k-means algorithm
def clustername(data, k, max_iter=100):
    centroids = initialSelection(data, k)
    for _ in range(max_iter):
        labels = assignClusterIds(data, centroids)
        new_centroids = computeClusterRepresentatives(data, labels, k)
        if np.allclose(centroids, new_centroids):
            break
        centroids = new_centroids
    return labels, centroids


# Bisecting k-means algorithm function
def bisecting_kmeans(data, k):
    clusters = [data]  # Start with the entire dataset as a single cluster
    labels = np.zeros(len(data), dtype=int)

    while len(clusters) < k:
       # Compute the sum of squares for each cluster
        sse_list = [computeSumOfSquares(cluster) for cluster in clusters]
        # Identify the cluster with the highest SSE to split
        to_split_index = np.argmax(sse_list)
        cluster_to_split = clusters.pop(to_split_index)

        # Split the selected cluster into two new clusters
        split_labels, _ = clustername(cluster_to_split, 2)
        new_cluster1 = cluster_to_split[split_labels == 0]
        new_cluster2 = cluster_to_split[split_labels == 1]


        # Only add new clusters if they contain points
        if len(new_cluster1) > 0 and len(new_cluster2) > 0:
            clusters.extend([new_cluster1, new_cluster2])
        else:
            print("Splitting failed. Ending early.")
            break

    # Assign labels to each point in the final list of clusters
    for idx, cluster in enumerate(clusters):
        cluster_labels = np.where((data[:, None] == cluster).all(-1))[0]
        labels[cluster_labels] = idx

    return labels

# Function to plot and save the silhouette scores
def plot_silhouette(k_values, silhouette_scores):
    plt.figure(figsize=(10, 6))
    plt.plot(k_values, silhouette_scores, 'bx-')
    plt.title('Silhouette Scores for Bisecting k-Means')
    plt.xlabel('Number of Clusters k')
    plt.ylabel('Silhouette Score')
    plt.grid(True)
    plt.savefig('silhouette_scores.png')
    plt.show()

if __name__ == "__main__":
    data = load_dataset("dataset")  # Make sure this matches your data file's name
    k_range = range(2, 10)  # Silhouette scores are not computed for k=1
    silhouette_scores = []

    for k in k_range:
        labels = bisecting_kmeans(data, k)
        if len(np.unique(labels)) > 1:
            score = silhouette_score(data, labels)
            silhouette_scores.append(score)
        else:
            print(f"Skipping silhouette score for k={k} due to insufficient unique clusters.")
            silhouette_scores.append(None)

    plot_silhouette(list(k_range), silhouette_scores)