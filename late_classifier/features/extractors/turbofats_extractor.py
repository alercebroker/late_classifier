from late_classifier.features.core.base import FeatureExtractorSingleBand
from turbofats import NewFeatureSpace
import logging


class TurboFatsFeatureExtractor(FeatureExtractorSingleBand):
    def __init__(self):
        self.features_keys = [
            'Amplitude', 'AndersonDarling', 'Autocor_length',
            'Beyond1Std',
            'Con', 'Eta_e',
            'Gskew',
            'MaxSlope', 'Mean', 'Meanvariance', 'MedianAbsDev',
            'MedianBRP', 'PairSlopeTrend', 'PercentAmplitude', 'Q31',
            'PeriodLS_v2',
            'Period_fit_v2', 'Psi_CS_v2', 'Psi_eta_v2', 'Rcs',
            'Skew', 'SmallKurtosis', 'Std',
            'StetsonK', 'Harmonics',
            'Pvar', 'ExcessVar',
            'GP_DRW_sigma', 'GP_DRW_tau', 'SF_ML_amplitude', 'SF_ML_gamma',
            'IAR_phi',
            'LinearTrend',
            'PeriodPowerRate'
        ]
        self.feature_space = NewFeatureSpace(self.features_keys)

    def _compute_features(self, detections, band=None, **kwargs):
        """
        Compute features for detections

        Parameters
        ----------
        detections :class:pandas.`DataFrame`
        kwargs

        Returns class:pandas.`DataFrame`
        Turbo FATS features.
        -------

        """
        index = detections.index.unique()[0]
        columns = self.get_features_keys(band)
        detections = detections[detections.fid == band]

        if band is None or len(detections) == 0:
            logging.error(
                f'Input dataframe invalid\n - Required columns: {self.required_keys}\n - Required one filter.')
            nan_df = self.nan_df(index)
            nan_df.columns = columns
            return nan_df
        return self.feature_space.calculate_features(detections)
