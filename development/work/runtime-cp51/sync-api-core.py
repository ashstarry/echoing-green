from pathlib import Path
import shutil
# CP51 changes only mood interpretation and bounded replies, not the simulation.
for name in ['atmosphere.mjs','gentle-reply.mjs']:
 shutil.copy2(Path('app/runtime-cp51/src')/name,Path('app/echoing-green-api/runtime')/name)
print('Synced only the two changed semantic modules; original API dependencies retained.')
