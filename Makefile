
PY   := python
GUI  := xvfb-run -a --server-args="-screen 0 1920x1080x16"
COV  := coverage run -a --source fluids

test:
	$(PY) -m fluids --time 100 -v 0 -o birdseye
	$(PY) -m fluids --time 100 -v 0 -o grid
	$(PY) -m fluids --time 100 -v 0 -o none
	$(GUI) $(PY) -m fluids --time 100 -v 99 -o birdseye
	$(GUI) $(PY) -m fluids --time 100 -v 99 -o grid
	$(GUI) $(PY) -m fluids --time 100 -v 99 -o none
	$(GUI) $(PY) tests/test_gym.py

	$(COV) -m fluids --time 100 -v 0 -o birdseye
	$(COV) -m fluids --time 100 -v 0 -o grid
	$(COV) -m fluids --time 100 -v 0 -o none
	$(GUI) $(COV) -m fluids --time 100 -v 99 -o birdseye
	$(GUI) $(COV) -m fluids --time 100 -v 99 -o grid
	$(GUI) $(COV) -m fluids --time 100 -v 99 -o none
	$(GUI) $(COV) tests/test_gym.py

