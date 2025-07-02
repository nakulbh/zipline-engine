from zipline.data.bundles import register
from zipline.data.bundles.csvdir import csvdir_equities
import pandas as pd

# Register the bundle 
register(
    'us-equities-bundle',
    csvdir_equities(['daily'], './data'),
    calendar_name='NYSE'
)

