.PHONY: config_encrypt config_decrypt export_deps


##########################
# CONFIGURATION FILES
##########################

# Constants
##########################
DECRYPTED_CONFIG_FILES= $(filter-out config/base.json config/test.json, $(wildcard config/*.json)) # Exclude base.json
ENCRYPTED_CONFIG_FILES= $(wildcard config/*.cast5)

# Rules
##########################
# Private task for echoing instructions
_pwd_prompt:
	@echo "Contact Rukmal Weerawarana for decryption password."

# to decrypt config vars
config_decrypt: _pwd_prompt
	@$(foreach f, $(ENCRYPTED_CONFIG_FILES), echo "\nDecrypting $(basename $(f))..." && openssl cast5-cbc -d -in $(f) -out $(basename $(f))${\n})

# to encrypt config vars
config_encrypt: _pwd_prompt
	@$(foreach f, $(DECRYPTED_CONFIG_FILES), echo "\nEncrypting $(f)..." && openssl cast5-cbc -e -in $(f) -out $(f).cast5${\n})


##########################
# PROJECT DEPENDENCIES
##########################

# Rule to generate and save the conda dependencies on for Windows deployment.
# The packages libedit, readline, libffi, libcxx, ncurses and libcxxabi are not
# available for windows and a thus removed from the resulting YAML file.
export_deps_win:
	conda env export --no-builds \
		| grep -v -e prefix \
		-e libedit \
		-e readline \
		-e libffi \
		-e libcxx \
		-e ncurses \
		-e libcxxabi \
		> conda/environment-windows.yml

# Rule to generate and save the conda dependencies for *nix deployment.
# The 'grep -v prefix' acts to remove the user's path from the exported file.
export_deps_nix:
	conda env export --no-builds \
		| grep -v prefix > conda/environment.yml

# Rule to export requirements.txt for pip.
export_deps_pip:
	pip freeze > requirements.txt

# Parent rule to export both *nix and Windows environment files.
export_deps: export_deps_nix export_deps_win export_deps_pip


# Other definitions
# =================
define \n


endef
