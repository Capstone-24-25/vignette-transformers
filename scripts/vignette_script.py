import numpy as np
import pandas as pd
import sklearn as sk
import matplotlib.pyplot as plt 
import seaborn as sns
from sklearn.cluster import KMeans
from scipy.stats import mode
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.utils import resample
from sklearn.decomposition import PCA

###############################################
# Manual Implementation of K-means Clustering #
###############################################

class kMeans():
    def __init__(self, K, X):
        self.K = K                                                                      # store K value 
        self.centroids = X[np.random.choice(X.shape[0], size=K, replace=False)]         # initialize random centroids 
        self.assignments = np.zeros(X.shape[0], dtype=int)                              # create vector to store assignments
        self.X = X                                                                      # store data

    def update_centroids(self, closest_centroids):
        """This function will update the stored centroids according to the new clusters"""
        X_grouped = [self.X[closest_centroids == idx] for idx in range(len(self.centroids))]        # group the datapoints into clusters by the centroids they are assigned to
        self.centroids = [X.mean(axis=0) for X in X_grouped]                                        # calculate the mean of each group to find the centroids of the centroids clusters
        
    def find_cluster(self): 
        """This method will iteratively search for clusters"""
        while True:                                                                                                # begin iteratively searching for clusters
            distances = np.array([np.linalg.norm(self.X - centroid, axis=1) for centroid in self.centroids]).T     # calculate the distance matrix; rows are data points, columns are clusters
            closest_centroids = np.argmin(distances, axis=1)                                                       # calculate the closest centroid to each data point

            if np.array_equal(closest_centroids,self.assignments):      # check for convergence
                break                                                   # break if we have converged to a solution
            else:
                self.update_centroids(closest_centroids)                # otherwise, update the stored centroids
                self.assignments = closest_centroids                    # store the current assignments

        return self.assignments        # return our solution
    

np.random.seed (0)                              # set a seed for reproducibility
X = np.random.standard_normal ((50 ,2))         # create simulated data
X[:25 ,0] += 3                                  # shift first dimension of the first 25 observations up by 3
X[:25 ,1] -= 4                                  # shift second dimension of the first 25 observations down by 4

cluster = kMeans(2, X)                          # instantiate class
predicted_labels = cluster.find_cluster()       # find the predicted labels 

true_labels = np.array([0] * 25 + [1] * 25)     # create the true labels 

label_mapping = {}                                                                      # instantiate the label mapping 
for cluster in np.unique(predicted_labels):                                             # iterate through each unique predicted cluster label
    cluster_indices = np.where(predicted_labels == cluster)[0]                          # get indices of data points in the current cluster
    most_common_label = mode(true_labels[cluster_indices], keepdims=True).mode[0]       # find the most common true label in the cluster    
    label_mapping[cluster] = most_common_label                                          # map the predicted cluster label to the most common true label

mapped_labels = np.array([label_mapping[label] for label in predicted_labels])          # map all predicted labels to their corresponding true labels

accuracy = np.sum(mapped_labels == true_labels) / len(true_labels)                      # calculate accuracy as the proportion of correctly classified labels

print(accuracy)       # print the calculated accuracy


#####################
# Practical Example #
#####################

red = pd.read_csv('data/winequality-red.csv', sep=';', header=0)        # load in red wine data
white = pd.read_csv('data/winequality-white.csv', sep=';', header=0)    # load in white wine data

red['color'] = 'red'                                                    # create color variable for red wine data
white['color'] = 'white'                                                # create color variable for white wine data

wine_data = pd.concat([red, white], axis=0)                             # combine both datasets into one
print(len(wine_data))                                                   # calculate the length of the datasets to confirm concatenation
print(pd.value_counts(wine_data['color']))                              # confirm the value counts of the red and white wine 

desired_white_count = int(len(red) * (60 / 40))            # Adjust white count to achieve 40-60 balance
white_downsampled = resample(                              # resample the white wine data to drop some observations
    white, 
    replace=False, 
    n_samples=desired_white_count, 
    random_state=42
)

wine_data = pd.concat([red, white_downsampled], axis=0)                                 # concatenate the datasets
wine_data = wine_data.sample(frac=1, random_state=42).reset_index(drop=True)            # shuffle the final dataset


correlation_matrix = wine_data.drop(columns=['color']).corr()                           # create correlation matrix of the quantitative data
plt.figure(figsize=(10, 8))                                                             # set the figure size
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', cbar=True)      # create the heatmap to present the matrix 
plt.title('Correlation Matrix of Wine Quality Dataset')                                 # title the figure
plt.show()                                                                              # show the figure 

wine_data = wine_data.drop(columns=['free sulfur dioxide'])                             # drop free sulfur dioxide, as that is directly related to another predictor


wine_data.hist(bins=20, figsize=(15, 10))                    # generates histograms for distribution of each variable
plt.show()                                                   # shows graph


def remove_extreme_outliers_iqr(data, column, multiplier=3):                                # defines a function to remove extreme outliers using the interquartile range (IQR)
    Q1 = data[column].quantile(0.25)                                                        # calculates the 25th percentile (first quartile) of the specified column
    Q3 = data[column].quantile(0.75)                                                        # calculates the 75th percentile (third quartile) of the specified column
    IQR = Q3 - Q1                                                                           # computes the interquartile range (IQR) as the difference between Q3 and Q1
    lower_bound = Q1 - multiplier * IQR                                                     # determines the lower bound for outliers based on the multiplier and IQR
    upper_bound = Q3 + multiplier * IQR                                                     # determines the upper bound for outliers based on the multiplier and IQR
    return data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]              # filters the data to include only values within the calculated bounds

columns_to_clean = ['fixed acidity', 'volatile acidity', 'chlorides', 'sulphates']          # cleans columns that still had large amounts of skewness even after transformation
for col in columns_to_clean:
    wine_data = remove_extreme_outliers_iqr(wine_data, col, multiplier=3)                   # remove outliers from all columns


numerical_columns = wine_data.select_dtypes(include=['number'])                             # finds all numerical columns in dataset
skewness = numerical_columns.skew()                                                         # calculates skewness of all numerical columns using Fisher-Pearson coefficient
print(skewness)                                                                             # prints out skewness

# Log transformation for heavy skew
log_transform_vars = ['residual sugar', 'fixed acidity', 'volatile acidity', 'chlorides']   # identifies which columns are heavily skewed and should be log transformed
for col in log_transform_vars:
    wine_data[col] = np.log1p(wine_data[col])                                               # loops through the columns and log transforms them

# Square root transformation for moderate skew
sqrt_transform_vars = ['sulphates', 'alcohol']         # identifies which columns are moderately skewed and should be square root transformed
for col in sqrt_transform_vars:
    wine_data[col] = np.sqrt(wine_data[col])           # loops through the columns and square root transforms them

skewness = numerical_columns.skew()                    # recalculates skewness 
print(skewness)                                        # prints out new skewness values after transformation


features = wine_data.drop(columns=['color'])                          # drop any non numerical columns for k-means application
scaler = StandardScaler()                                             # standardizes features
wine_scaled = scaler.fit_transform(features)                          # applies standardization to wine data

# Apply PCA to reduce dimensions
pca = PCA(n_components=2)                                             # Reduce to 2 dimensions for clustering and visualization
wine_pca = pca.fit_transform(wine_scaled)                             # Transform the scaled data using PCA

explained_variance = pca.explained_variance_ratio_                    # captures the proportion of variance explained by each principal component

print(f"Explained Variance by each component: {explained_variance}")  # print the explained variance ratio

kmeans = KMeans(n_clusters=2, init='k-means++', random_state=42)      # initializes k-means model with 2 clusters
kmeans.fit(wine_pca)                                                  # fits kmeans to wine_scaled data

wine_data['cluster'] = kmeans.labels_                                 # adds k-means cluster labels

print("Inertia:", kmeans.inertia_)                                    # prints out inertia score of model
silhouette_avg = silhouette_score(wine_pca, kmeans.labels_)           # calculates average silhouette score
print("Silhouette Score:", silhouette_avg)                            # prints out silhouette score

# visualizes clusters
plt.scatter(wine_pca[:, 0], wine_pca[:, 1], c=kmeans.labels_, cmap='viridis')                                   # plots data points and colors them based on cluster label
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=300, c='red', label='Centroids')    # plots cluster centroids in red 
plt.xlabel("Feature 1")                                                                                         # labels x axis
plt.ylabel("Feature 2")                                                                                         # labels y axis
plt.title("K-means Clustering")                                                                                 # adds title
plt.legend()                                                                                                    # adds legend
plt.show()                                                                                                      # shows plot

# calculate accuracy of k-means model
total_wines = wine_data.shape[0]                            # gets the total number of wines in the dataset
correctly_classified = 1469 + 2323                          # sums up the wines correctly classified into clusters
accuracy = correctly_classified / total_wines               # calculates clustering accuracy as the ratio of correctly classified wines to total wines
print(f"Clustering accuracy: {accuracy * 100:.2f}%")        # prints clustering accuracy as a percentage with two decimal places
