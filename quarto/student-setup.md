# Running the census example yourself

The lecture's live demo is the HoloViz **Census 2010** example: datashader over all
306,675,004 people of the 2010 US census. This guide gets it running on your own
machine. It assumes Windows 11 with WSL2; on Linux or macOS, skip step 1 and use a
normal terminal.

Budget: roughly **8 GB of free disk** and ideally **16 GB of RAM** (see step 8).
- The conda environment is about 2.6 GB on the lecture machine, and conda's package
  cache adds more.
- The data takes 1.4 GB to download plus 2.2 GB unpacked.

## 1. WSL2 (Windows only)

In PowerShell **as administrator**:

```powershell
wsl --install
```

Restart when asked. This installs WSL2 with Ubuntu. It needs Windows 10 version 2004
(build 19041) or later, or Windows 11. Then open **Ubuntu** from the Start menu. Every
command below runs in that Linux terminal, not in PowerShell.

Details: <https://learn.microsoft.com/en-us/windows/wsl/install>

## 2. Keep the project on the Linux side

Work in your Linux home directory (`~/census`), **not** under `/mnt/c/...`. Microsoft's
own advice: "For the fastest performance speed, store your files in the WSL file system
if you are working in a Linux command line." Reading 2 GB of Parquet files through the
Windows-drive bridge is slow. And if that Windows folder is synced (OneDrive and the
like), the sync client will also try to upload the data.

Details: <https://learn.microsoft.com/en-us/windows/wsl/filesystems>

## 3. Miniforge (conda, from conda-forge)

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

Accept the licence and let the installer initialise conda. Then close and reopen the
terminal.

Details: <https://github.com/conda-forge/miniforge>

## 4. The notebook: HoloViz's "Download project" bundle

The example's page, <https://examples.holoviz.org/gallery/census/census.html>, has a
**Download project** button. From the terminal:

```bash
mkdir -p ~/census && cd ~/census
curl -L -O https://examples.holoviz.org/_static/census.zip
python -m zipfile -e census.zip .
cd census
```

The bundle holds `census.ipynb`, `anaconda-project.yml` (with a lock file) and a README,
but **no data**. Its own recipe (`anaconda-project run`) pins 2023-era versions (Python
3.10, Dask 2023.5, datashader 0.15). We use a current environment instead (next step).

## 5. The environment

Save this as `environment.yml` in `~/census/census`. It is the lecture's own
`environment.yml`, minus Quarto (only needed for the slides), plus JupyterLab:

```yaml
name: census
channels:
  - conda-forge
dependencies:
  - python=3.12
  - datashader>=0.16
  - holoviews>=1.19
  - panel>=1.5
  - dask>=2024.1
  - pyarrow
  - colorcet
  - xyzservices
  - matplotlib
  - jupyterlab
```

```bash
conda env create -f environment.yml
conda activate census
```

## 6. The data

```bash
curl -L -O https://s3.amazonaws.com/datashader-data/census2010.parq.zip   # 1.4 GB
python -m zipfile -e census2010.parq.zip data/                           # 2.2 GB unpacked
rm census2010.parq.zip
```

You should now have `data/census2010.parq/`, a folder of Parquet files.

## 7. Two fixes in the notebook

**The read (required).** The first code cell says

```python
df = dd.read_parquet('./data/census2010.parq', engine='fastparquet')
df = df.categorize('race')
df = df.persist()
```

Change the first line to

```python
df = dd.read_parquet('./data/census2010.parq', categories=[])
```

and keep the other two. Why:

- Dask deprecated its `fastparquet` engine in version 2024.1.0 and has since removed it.
  Current versions stop with "Fastparquet engine is not supported".
- The default engine (pyarrow) then trips over how these fastparquet-written files
  describe the `race` column, and stops with "Not all columns are categoricals".
- `categories=[]` asks for no categorical columns at read time, so `race` comes in as
  plain values. The next line, `df.categorize('race')`, rebuilds the categories with one
  pass over the data.

**The map labels (only if they don't show).** The interactive maps near the end overlay
CartoDB's label tiles (`xyz.CartoDB.PositronOnlyLabels()`). If the city names don't
appear, use Esri's public reference layer instead, which the lecture uses:

```python
labels = hv.Tiles("https://server.arcgisonline.com/ArcGIS/rest/services/Reference/"
                  "World_Boundaries_and_Places/MapServer/tile/{Z}/{Y}/{X}")
```

## 8. Memory

- `.persist()` loads all 306 M rows into RAM, which makes every later step fast. The
  notebook's own advice: with less than 16 GB of RAM, delete the `.persist()` line. Dask
  then works out of core: much slower, but it runs on small machines.
- **WSL2 gets only half of Windows' RAM by default**, so a 16 GB laptop gives Linux
  about 8 GB. To give it more, create `%UserProfile%\.wslconfig` on the Windows side:

  ```ini
  [wsl2]
  memory=12GB
  ```

  Then run `wsl --shutdown` in PowerShell and reopen Ubuntu.

  Details: <https://learn.microsoft.com/en-us/windows/wsl/wsl-config>

## 9. Run it

```bash
cd ~/census/census
conda activate census
jupyter lab
```

Open the printed `http://localhost:8888/...` link in your Windows browser. WSL forwards
localhost, so it just works. Then open `census.ipynb` and run the cells in order. The
first cell (loading and `persist()`) takes a while; everything after it is quick.
