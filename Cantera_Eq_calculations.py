import cantera as ct
print(ct.__version__)


# import cantera as ct
# print('Available files:', ct.datadir)
# # Or directly load it
# gas = ct.Solution('nDodecane_Reitz.yaml')
# print('Fuel species:', gas.fuel_species)

import pkg_resources

# check which files are available
# # Locate the Cantera data directory
# data_path = pkg_resources.resource_filename('cantera', 'data')
# print("Cantera data directory:", data_path)

# # List all mechanism files there
# import os
# files = [f for f in os.listdir(data_path) if f.endswith(('.yaml', '.cti'))]
# print("Available mechanisms:\n ", "\n  ".join(files))

# Create a gas object with GRI-Mech 3.0 or your mechanism
gas = ct.Solution('nDodecane_Reitz.yaml')
# print("All species:", gas.species_names)

# Define stoichiometric diesel-air mixture (use C12H23 for diesel)
gas.TP = 1800, 2e7  # T in K, P in Pa
gas.set_equivalence_ratio(phi=0.4, fuel='c12h26', oxidizer={'o2':1.0, 'n2':3.76})

# Equilibrate at constant T, P
gas.equilibrate('TP')

# Print equilibrium concentrations
for species in ['co2', 'h2O', 'co', 'o2', 'n2']:
    print(f"{species}: {gas.concentrations[gas.species_index(species)]:.3e} mol/cm³")