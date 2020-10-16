from typing import List

from ..core.base import FeatureExtractor
from astropy.coordinates import SkyCoord
import pandas as pd
import numpy as np
import logging


class GalacticCoordinatesExtractor(FeatureExtractor):
    def get_features_keys(self) -> List[str]:
        return ['gal_b', 'gal_l']

    def get_required_keys(self) -> List[str]:
        return ['ra', 'dec']

    def _compute_features(self, detections, **kwargs):
        """

        Parameters
        ----------
        detections :class:pandas.`DataFrame`
        DataFrame with detections of an object.
        kwargs Not required.

        Returns :class:pandas.`DataFrame`
        -------

        """

        radec_df = detections[['ra', 'dec']].groupby(level=0).mean()
        coordinates = SkyCoord(
            ra=radec_df['ra'],
            dec=radec_df['dec'],
            frame='icrs',
            unit='deg')
        galactic = coordinates.galactic
        np_galactic = np.stack((galactic.b.degree, galactic.l.degree), axis=-1)
        galactic_coordinates_df = pd.DataFrame(
            np_galactic,
            index=radec_df.index,
            columns=['gal_b', 'gal_l'])
        galactic_coordinates_df.index.name = 'oid'
        return galactic_coordinates_df
