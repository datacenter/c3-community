export DEBIAN_FRONTEND=noninteractive
sudo sed -i -e '/cliqr/s/^/#/' /etc/apt/sources.list
sudo apt-get -y update
sudo apt-get -y install python-numpy python-scipy python-dev python-pip python-nose g++ git libatlas3gf-base libatlas-dev libhdf5-7 libhdf5-dev python3-matplotlib
sudo add-apt-repository -y ppa:fkrull/deadsnakes-python2.7
sudo apt-get -y update
sudo apt-get -y --force-yes install python2.7
sudo pip install --upgrade pip
sudo pip install theano keras tensorflow pyyaml cython h5py ipython jupyter matplotlib
mkdir /home/cliqruser/keras
git clone https://github.com/leriomaggio/deep-learning-keras-tensorflow /home/cliqruser/keras/
jupyter notebook --no-browser --ip=0.0.0.0 --FileContentsManager.root_dir=/home/cliqruser/keras/  --NotebookApp.token='' &