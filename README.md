# Computational neuroscience

[Spike-rate analysis by stimulus condition](Analysis-of-Orientation-Tuning-in-V1-Neurons/README.md)

An educational workflow for a supplied CRCNS pvc-11 MATLAB file. It computes trial-averaged spike rates and descriptive SEM across trials. It uses condition indices by default; orientation or direction labels require an explicit, verified mapping.

```bash
git clone https://github.com/Fatima3722/Computational_Neuroscience.git
cd Computational_Neuroscience
python -m pip install -r requirements.txt
python Analysis-of-Orientation-Tuning-in-V1-Neurons/analyze_v1_tuning.py --demo --output outputs/demo
python -m unittest discover -s tests -v
```

Tested with Python 3.12.14 and the pinned scientific dependencies. The included demo is synthetic, with fixed seed 42. Six checks cover known spike counts, a generated MATLAB round trip, empty spike trains, one-trial SEM, invalid data, condition-angle mapping and command-line success/failure behaviour. Real CRCNS recordings were not available for this revision, so the complete real-data workflow has not been independently reproduced here.
