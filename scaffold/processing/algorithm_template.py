"""Template for a QGIS Processing Algorithm."""

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication


class AntigravityAlgorithm(QgsProcessingAlgorithm):
    """
    Template algorithm for Antigravity-powered plugins.
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):  # noqa: N802
        return AntigravityAlgorithm()

    def name(self):
        return "antigravity_algorithm"

    def displayName(self):  # noqa: N802
        return self.tr("Antigravity Algorithm")

    def group(self):
        return self.tr("Antigravity Scripts")

    def groupId(self):  # noqa: N802
        return "antigravity"

    def shortHelpString(self):  # noqa: N802
        return self.tr("Example algorithm showing the standard structure.")

    def initAlgorithm(self, config=None):  # noqa: N802
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr("Input layer"),
                [QgsProcessing.TypeVectorAnyGeometry],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr("Output layer"))
        )

    def processAlgorithm(self, parameters, context, feedback):  # noqa: N802
        # Implementation goes here
        source = self.parameterAsSource(parameters, self.INPUT, context)
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs(),
        )

        # Logic loop example
        feedback.pushInfo(f"Processing layer: {source.sourceName()}")

        return {self.OUTPUT: dest_id}
