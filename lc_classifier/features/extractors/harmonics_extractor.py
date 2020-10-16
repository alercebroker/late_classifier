from typing import List

import numpy as np
import pandas as pd
import logging

from ..core.base import FeatureExtractorSingleBand
from ..extractors import PeriodExtractor


class HarmonicsExtractor(FeatureExtractorSingleBand):
    def __init__(self):
        self.n_harmonics = 7

    def compute_feature_in_one_band(self, detections: pd.DataFrame, band=None, **kwargs) -> pd.DataFrame:
        if ('shared_data' in kwargs.keys() and
                'period' in kwargs['shared_data'].keys()):
            periods = kwargs['shared_data']['period']
        else:
            logging.info('Harmonics extractor was not provided with period '
                         'data, so a periodogram is being computed')
            period_extractor = PeriodExtractor()
            periods = period_extractor.compute_features(detections)

        oids = detections.index.unique()
        features = []
        for oid in oids:
            oid_detections = detections.loc[[oid]]
            if band not in oid_detections.fid.values:
                logging.info(
                    f'extractor=Harmonics extractor object={oid} '
                    f'required_cols={self.get_required_keys()}  band={band}')
                features.append([np.nan] * len(self.get_features_keys()))
                continue

            oid_band_detections = oid_detections[oid_detections.fid == band]

            magnitude = oid_band_detections['magpsf_ml'].values
            time = oid_band_detections['mjd'].values
            error = oid_band_detections['sigmapsf_ml'].values + 10 ** -2

            try:
                period = periods[['Multiband_period']].loc[[oid]].values.flatten()
                best_freq = 1 / period

                omega = [np.array([[1.] * len(time)])]
                timefreq = (2.0 * np.pi * best_freq * np.arange(1, self.n_harmonics + 1)).reshape(1, -1).T * time
                omega.append(np.cos(timefreq))
                omega.append(np.sin(timefreq))
                omega = np.concatenate(omega, axis=0).T  # Omega.shape == (lc_length, 1+2*self.n_harmonics)
                inverr = 1.0 / error

                # weighted regularized linear regression
                w_a = inverr.reshape(-1, 1) * omega
                w_b = (magnitude * inverr).reshape(-1, 1)
                coeffs = np.matmul(np.linalg.pinv(w_a), w_b).flatten()
                fitted_magnitude = np.dot(omega, coeffs)
                coef_cos = coeffs[1:self.n_harmonics + 1]
                coef_sin = coeffs[self.n_harmonics + 1:]
                coef_mag = np.sqrt(coef_cos ** 2 + coef_sin ** 2)
                coef_phi = np.arctan2(coef_sin, coef_cos)

                # Relative phase
                coef_phi = coef_phi - coef_phi[0] * np.arange(1, self.n_harmonics + 1)
                coef_phi = coef_phi[1:] % (2 * np.pi)

                mse = np.mean((fitted_magnitude - magnitude) ** 2)
                features.append(
                    np.concatenate([coef_mag, coef_phi, np.array([mse])]).tolist())
            except Exception as e:
                logging.error(f'KeyError in HarmonicsExtractor, period is not '
                              f'available: oid {oid}\n{e}')
                features.append([np.nan]*len(self.get_features_keys()))
                continue

        features = pd.DataFrame(
            data=np.array(features),
            columns=self.get_features_keys_with_band(band),
            index=oids)
        return features

    def get_features_keys(self) -> List[str]:
        feature_names = ['Harmonics_mag_%d' % (i+1) for i in range(self.n_harmonics)]
        feature_names += ['Harmonics_phase_%d' % (i+1) for i in range(1, self.n_harmonics)]
        feature_names.append('Harmonics_mse')
        return feature_names

    def get_required_keys(self) -> List[str]:
        return [
            'mjd',
            'magpsf_ml',
            'fid',
            'sigmapsf_ml'
        ]