
PY   := python
GUI  := xvfb-run -a --server-args="-screen 0 1920x1080x16"
COV  := coverage run -a --source fluids

test: clean
	$(PY) -m fluids --time 100 -v 0 -o birdseye --datasaver="~/data/fluids_data"
	$(PY) -m fluids --time 100 -v 0 -o grid --datasaver="~/data/fluids_data"
	$(PY) -m fluids --time 100 -v 0 -o none --datasaver="~/data/fluids_data"
	$(PY) -m fluids --time 100 -v 0 -o qlidar --datasaver="~/data/fluids_data"
	$(GUI) $(PY) -m fluids --time 100 -v 99 -o birdseye --datasaver="~/data/fluids_data"
	$(GUI) $(PY) -m fluids --time 100 -v 99 -o grid --datasaver="~/data/fluids_data"
	$(GUI) $(PY) -m fluids --time 100 -v 99 -o none --datasaver="~/data/fluids_data"
	$(GUI) $(PY) -m fluids --time 100 -v 0 -o qlidar --datasaver="~/data/fluids_data"
	$(GUI) $(PY) tests/test_gym.py 
	$(GUI) $(PY) tests/test_gym_supervisor.py
	$(GUI) $(PY) tests/test_grid_obs.py
coverage: clean
	$(COV) -m fluids --time 100 -v 0 -o birdseye --datasaver="~/data/fluids_data"
	$(COV) -m fluids --time 100 -v 0 -o grid --datasaver="~/data/fluids_data"
	$(COV) -m fluids --time 100 -v 0 -o none --datasaver="~/data/fluids_data"
	$(COV) -m fluids --time 100 -v 0 -o qlidar --datasaver="~/data/fluids_data"
	$(GUI) $(COV) -m fluids --time 100 -v 99 -o birdseye --datasaver="~/data/fluids_data"
	$(GUI) $(COV) -m fluids --time 100 -v 99 -o grid --datasaver="~/data/fluids_data"
	$(GUI) $(COV) -m fluids --time 100 -v 99 -o none --datasaver="~/data/fluids_data"
	$(GUI) $(COV) -m fluids --time 100 -v 99 -o qlidar --datasaver="~/data/fluids_data"
	$(GUI) $(COV) tests/test_gym.py
	$(GUI) $(COV) tests/test_gym_supervisor.py
	$(GUI) $(COV) tests/test_grid_obs.py


clean:
	rm -rf ~/.fluidscache
	rm -rf ~/data
