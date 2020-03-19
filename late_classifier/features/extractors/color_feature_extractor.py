from late_classifier.features.core.base import FeatureExtractor
import pandas as pd


class ColorFeatureComputer(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.features_keys = ['g-r_max', 'g-r_mean']

    def compute_features(self, detections, **kwargs):
        """
        Parameters
        ----------
        detections :class:pandas.`DataFrame`
        DataFrame with detections of an object.

        kwargs Not required.

        Returns :class:pandas.`DataFrame`
        -------
        """
        g_band_mag = detections[detections.fid == 1]['magpsf_corr']
        r_band_mag = detections[detections.fid == 2]['magpsf_corr']
        g_r_max = g_band_mag.groupby(level=0).min() - r_band_mag.groupby(level=0).min()
        g_r_max.rename('g-r_max', inplace=True)
        g_r_mean = g_band_mag.groupby(level=0).mean() - r_band_mag.groupby(level=0).mean()
        g_r_mean.rename('g-r_mean', inplace=True)
        features = pd.concat([g_r_max, g_r_mean], axis=1)
        return features