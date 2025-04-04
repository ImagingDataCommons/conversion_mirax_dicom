import pydicom
from pathlib import Path
from wsidicomizer import WsiDicomizer
from wsidicomizer.metadata import WsiDicomizerMetadata


def wsidicomizer_convert(input_file: Path, output_folder: Path, metadata: WsiDicomizerMetadata, additional_metadata: pydicom.Dataset) -> None: 
    _ = WsiDicomizer.convert(
        filepath=input_file,
        output_path=output_folder,
        metadata=metadata,
        metadata_post_processor=additional_metadata,
        tile_size=1024, # wsidicom seems to not be able to infer tile size from mrxs automatically, so will use this one provided here.
        include_levels=[0,2,4,6,8,10], 
        include_label=False, 
        include_overview=True, 
        workers=4, 
        offset_table='eot'
    )