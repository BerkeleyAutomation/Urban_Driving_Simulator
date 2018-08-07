
PY   := python
GUI  := xvfb-run -a --server-args="-screen 0 1920x1080x16"
COV  := coverage run -a --source fluids

test: clean
	$(PY) -m fluids --time 100 -v 0 -o birdseye
	$(PY) -m fluids --time 100 -v 0 -o grid
	$(PY) -m fluids --time 100 -v 0 -o none
	$(GUI) $(PY) -m fluids --time 100 -v 99 -o birdseye
	$(GUI) $(PY) -m fluids --time 100 -v 99 -o grid
	$(GUI) $(PY) -m fluids --time 100 -v 99 -o none
	$(GUI) $(PY) tests/test_gym.py
	$(GUI) $(PY) tests/test_gym_supervisor.py
	$(GUI) $(PY) tests/test_grid_obs.py
coverage: clean
	$(COV) -m fluids --time 100 -v 0 -o birdseye
	$(COV) -m fluids --time 100 -v 0 -o grid
	$(COV) -m fluids --time 100 -v 0 -o none
	$(GUI) $(COV) -m fluids --time 100 -v 99 -o birdseye
	$(GUI) $(COV) -m fluids --time 100 -v 99 -o grid
	$(GUI) $(COV) -m fluids --time 100 -v 99 -o none
	$(GUI) $(COV) tests/test_gym.py
	$(GUI) $(COV) tests/test_gym_supervisor.py
	$(GUI) $(COV) tests/test_grid_obs.py


clean:
	rm -rf ~/.fluidscache
