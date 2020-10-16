import sys
import pandas as pd
from late_classifier.features import DetectionsPreprocessorZTF


detections = pd.read_pickle(sys.argv[1])
non_detections = pd.read_pickle(sys.argv[2])

preprocessor_ztf = DetectionsPreprocessorZTF()
detections = preprocessor_ztf.preprocess(detections)

oid_intersection = detections.index.unique().intersection(
    non_detections.index.unique())

non_detections = non_detections.loc[oid_intersection]

detections.to_pickle(sys.argv[3])
non_detections.to_pickle(sys.argv[4])
