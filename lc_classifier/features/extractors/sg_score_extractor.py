from typing import List

from ..core.base import FeatureExtractor
from pandas import DataFrame


class SGScoreExtractor(FeatureExtractor):
    def get_features_keys(self) -> List[str]:
        return ['sgscore1']

    def get_required_keys(self) -> List[str]:
        return ['sgscore1']

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
        sgscore_medians = detections[['sgscore1']].groupby(level=0).median()
        return sgscore_medians


class StreamSGScoreExtractor(FeatureExtractor):
    def get_features_keys(self) -> List[str]:
        return []

    def get_required_keys(self) -> List[str]:
        return []

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
        metadata = kwargs["metadata"]
        oids = detections.index.unique()
        df_sgscore = metadata[["oid", "sgscore1"]]
        df_sgscore.drop_duplicates("oid", inplace=True)
        df_sgscore.set_index("oid", inplace=True)
        return df_sgscore.loc[oids]
