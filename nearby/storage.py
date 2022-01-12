from pipeline.storage import PipelineMixin
from whitenoise.storage import CompressedStaticFilesStorage


class WhitenoiseCompressedPipelineStorage(PipelineMixin, CompressedStaticFilesStorage):
    pass
