import subprocess

# Install configobj
subprocess.run(["pip", "install", "configobj"])

# Download and extract cdcl_pascal_model.zip
subprocess.run(["wget", "https://www.dropbox.com/s/6ttxi3vb6e7kx4t/cdcl_pascal_model.zip?dl=1", "-O", "cdcl_pascal_model.zip"])
subprocess.run(["unzip", "cdcl_pascal_model.zip", "-d", "weights"])
subprocess.run(["rm", "cdcl_pascal_model.zip"])

# Download and extract cdcl_model.zip
subprocess.run(["wget", "https://www.dropbox.com/s/sknafz1ep9vds1r/cdcl_model.zip?dl=1", "-O", "cdcl_model.zip"])
subprocess.run(["unzip", "cdcl_model.zip", "-d", "weights"])
subprocess.run(["rm", "cdcl_model.zip"])

# Create input and output directories
subprocess.run(["mkdir", "input"])
subprocess.run(["mkdir", "output"])

# Move all .png files to the input directory
subprocess.run(["mv", "*.png", "input/"])
