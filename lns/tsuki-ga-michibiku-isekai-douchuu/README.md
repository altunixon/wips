#### Trash ads
```bash
ls -1 | xargs -I {} sed -i '/__ATA\.cmd\.push/,/\}\);/d' "{}"
```
