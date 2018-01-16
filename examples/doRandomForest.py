import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

#######################################################################################################################
# Machine learning on the datasets to identify the city center
# The cities chosen were Pau and Saint Malo for the learning part, and Vernon for the test
#######################################################################################################################

# Grid size on which to do the machine learning.
# Possibility to test for several sizes at the same time, in the same file
_GRID_SIZE = [100]

# CSV file with for columns longitude, latitude and value fot the feature
# Per grid size
_TRAIN_FILES = {
    100: {'light_pollution': ['data/light_pollution_Pau100.csv',
                              'data/light_pollution_SaintMalo100.csv'
                              ],
          'roads_centroids': ['data/roads_centroids_Pau100.csv',
                              'data/roads_centroids_SaintMalo100.csv'
                              ]},
    250: {'light_pollution': ['data/light_pollution_Pau250.csv',
                              'data/light_pollution_SaintMalo250.csv'
                              ],
          'roads_centroids': ['data/roads_centroids_Pau250.csv',
                              'data/roads_centroids_SaintMalo250.csv'
                              ]},
    500: {'light_pollution': ['data/light_pollution_Pau500.csv',
                              'data/light_pollution_SaintMalo500.csv'
                              ],
          'roads_centroids': ['data/roads_centroids_Pau500.csv',
                              'data/roads_centroids_SaintMalo500.csv'
                              ]}
}

_TEST_FILES = {
    100: {'light_pollution': ['data/light_pollution_Vernon100.csv'],
          'roads_centroids': ['data/roads_centroids_Vernon100.csv']},
    250: {'light_pollution': ['data/light_pollution_Vernon250.csv'],
          'roads_centroids': ['data/roads_centroids_Vernon250.csv']},
    500: {'light_pollution': ['data/light_pollution_Vernon500.csv'],
          'roads_centroids': ['data/roads_centroids_Vernon500.csv']}

}

# City centers coordinates for training datasets and test dataset
_TRAIN_CENTERS = {
    100: [(-2.025110591047195, 48.648479095087275),  # Saint-Malo grid 100
          (-1.991415197883358, 48.62379763174175),
          (-1.9702824220181299, 48.65804657464772),
          (-0.3681094553073088, 43.29465539949739)],  # Pau grid 100
    250: [(-2.0259203399307473, 48.64979585596023),  # Saint-Malo grid 250
          (-1.9928127433778988, 48.62418814264638),
          (-1.9690152610430356, 48.65900190690825),
          (-0.36746907175118265, 43.29422371565527),  # Pau grid 250
          ],
    500: [(-2.022313698851133, 48.647698839716924),  # Saint-Malo grid 500
          (-1.9925932871627279, 48.62194464309053),
          (-1.9690152610430356, 48.65900190690825),
          (-0.37067107963379153, 43.296382098714915)]  # Pau grid 500
}

_TEST_CENTERS = {
    100: [(1.48555175529991, 49.107790192861714),
          (1.4828128634458346, 49.10775428386435)],
    250: [(1.486921202706036, 49.10780812303236),
          (1.4834975860393032, 49.10776326719569)],
    500: [(1.486921202706036, 49.10780812303236),
          (1.4800739755419279, 49.107718309992386)]
}


# Gets the dataframe of all features for each coordinate
def _getAlldataDataframe(files_dict, centers):
    script_dir = os.path.dirname(__file__)

    dfs_light_poll = [pd.read_csv(os.path.join(script_dir, file), sep=',', converters={'longitude': float,
                                                                                       'latitude': float})
                          .set_index(['longitude', 'latitude'])
                      for g in _GRID_SIZE
                      for file in files_dict[g]['light_pollution']]
    dfs_roads_cent = [pd.read_csv(os.path.join(script_dir, file), sep=',', converters={'longitude': float,
                                                                                       'latitude': float})
                          .set_index(['longitude', 'latitude'])
                      for g in _GRID_SIZE
                      for file in files_dict[g]['roads_centroids']]

    df1 = dfs_light_poll[0].append([dfs_light_poll[i] for i in range(1, len(dfs_light_poll))])  \
        if len(dfs_light_poll) > 1 else dfs_light_poll[0]
    df2 = dfs_roads_cent[0].append([dfs_roads_cent[i] for i in range(1, len(dfs_roads_cent))])  \
        if len(dfs_roads_cent) > 1 else dfs_roads_cent[0]

    df = df1.join(df2).drop_duplicates()

    all_centers = []
    for i in _GRID_SIZE:
        all_centers += centers[i]

    df['is_citycenter'] = [1 if coord in all_centers else 0 for coord in df.index.values]

    return df


if __name__ == "__main__":
    df_train = _getAlldataDataframe(_TRAIN_FILES, _TRAIN_CENTERS)
    df_test = _getAlldataDataframe(_TEST_FILES, _TEST_CENTERS)
    features = df_train.columns[:2]
    clf = RandomForestClassifier(n_jobs=2, random_state=0)
    clf.fit(df_train[features], df_train.is_citycenter.values)
    predictions = clf.predict(df_test[features])
    predict_proba = clf.predict_proba(df_test[features])
    print(accuracy_score(df_test.is_citycenter.values, predictions))
    print(confusion_matrix(df_test.is_citycenter.values, predictions))
    print(list(zip(df_train[features], clf.feature_importances_)))