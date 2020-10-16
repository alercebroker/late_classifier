from typing import List

from ..core.base import FeatureExtractorSingleBand
from turbofats import FeatureSpace
import pandas as pd
import logging


class TurboFatsFeatureExtractor(FeatureExtractorSingleBand):
    def __init__(self):
        self.feature_space = FeatureSpace(self._feature_keys_for_new_feature_space())
        self.feature_space.data_column_names = ['magpsf_ml', 'mjd', 'sigmapsf_ml']

    def _feature_keys_for_new_feature_space(self):
        return [
            'Amplitude', 'AndersonDarling', 'Autocor_length',
            'Beyond1Std',
            'Con', 'Eta_e',
            'Gskew',
            'MaxSlope', 'Mean', 'Meanvariance', 'MedianAbsDev',
            'MedianBRP', 'PairSlopeTrend', 'PercentAmplitude', 'Q31',
            'Rcs',
            'Skew', 'SmallKurtosis', 'Std',
            'StetsonK',
            'Pvar', 'ExcessVar',
            'GP_DRW_sigma', 'GP_DRW_tau', 'SF_ML_amplitude', 'SF_ML_gamma',
            'IAR_phi',
            'LinearTrend',
        ]

    def get_features_keys(self) -> List[str]:
        features_keys = self._feature_keys_for_new_feature_space()
        return features_keys

    def get_required_keys(self) -> List[str]:
        return ['mjd', 'magpsf_ml', 'fid', 'sigmapsf_ml']

    def compute_feature_in_one_band(self, detections, band=None, **kwargs):
        """
        Compute features from turbo-fats.
        Parameters
        ----------
        detections : pd.DataFrame
            Light curve from a single band and a single object.
        band : int
            Number of the band of the light curve.
        kwargs
        Returns
        ------
        pd.DataFrame
            turbo-fats features (one-row dataframe).
        """
        oids = detections.index.unique()
        features = []

        detections = detections.sort_values('mjd')

        columns = self.get_features_keys_with_band(band)
        for oid in oids:
            oid_detections = detections.loc[[oid]]
            if band not in oid_detections.fid.values:
                logging.info(
                    f'extractor=TURBOFATS object={oid} required_cols={self.get_required_keys()} band={band}')
                nan_df = self.nan_df(oid)
                nan_df.columns = columns
                features.append(nan_df)
                continue

            oid_band_detections = oid_detections[oid_detections.fid == band]

            object_features = self.feature_space.calculate_features(oid_band_detections)
            object_features = pd.DataFrame(
                data=object_features.values,
                columns=[f'{c}_{band}' for c in object_features.columns],
                index=object_features.index
            )
            features.append(object_features)
        features = pd.concat(features, axis=0, sort=True)
        features.index.name = 'oid'
        return features
