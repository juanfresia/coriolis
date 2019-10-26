
# Call the proper docker build
build_cpp build_python build_rust:
	@echo "Building CORIOLIS image for $(patsubst build_%,%,$@) language"
	@cd $(patsubst build_%,%,$@) && docker build . -t coriolis_$(patsubst build_%,%,$@):latest

all: build_cpp build_python build_rust
	@echo "Done building!"

rm_cpp rm_python rm_rust:
	@echo "Removing CORIOLIS image for $(patsubst rm_%,%,$@) language"
	@docker image rm coriolis_$(patsubst rm_%,%,$@)

clean: rm_cpp rm_python rm_rust
	@echo "Done cleaning!"