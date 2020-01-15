from pathlib import Path

proj_dir = Path(__file__).parent.parent.parent
media_dir = proj_dir / Path("run/media")

s3_storage = "s3:/..."
local_storage = f"local:{media_dir}"
