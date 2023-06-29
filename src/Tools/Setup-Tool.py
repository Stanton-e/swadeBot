#----------------------------------------------------
#           Requirements Installer & Updater
#                       by
#                     Stan44
#       Modify as needed if you have issues
#----------------------------------------------------
import os
import subprocess
import sys

# Installs the required packages to run your program
def install_or_update_requirements():
    main_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(main_directory)
    requirements_file = os.path.join(parent_directory, 'requirements.txt')
    print('Installing or updating requirements, please wait...')
    with open(requirements_file, 'r') as file:
        requirements = file.readlines()
    requirements = [req.strip() for req in requirements]

    # Ask the user if they want to skip checking for dependencies and updates
    skip_check = input("Do you want to skip checking for dependencies and updates? (y/n): ")
    if skip_check.lower() == 'y':
        print("Skipping checking for dependencies and updates...")
        return True

    for requirement in requirements:
        try:
            result = subprocess.run(['pip', 'show', requirement], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Requirement '{requirement}' is already installed.")
            else:
                print(f"Requirement '{requirement}' is not installed.")
                subprocess.run(['pip', 'install', requirement], check=True)
        except Exception as e:
            print("An error occurred while checking or installing the package:", str(e))
            continue

        try:
            result = subprocess.run(['pip', 'install', '--upgrade', requirement], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Requirement '{requirement}' is up to date.")
            else:
                print(f"An error occurred while updating the requirement '{requirement}'.")
        except Exception as e:
            print("An error occurred while checking or updating the package:", str(e))
            continue

    return False

# Call the requirements installer/updater function
skip = install_or_update_requirements()

if skip:
    print("Skipping dependencies and updates.")
    # Add any necessary code when skipping the dependencies and updates

# Add your main program code here
print("Continuing with the main program...")



#-----------------------------------------------------
#        Original source by stan version 0.1
#             for historical reasons
#------------------------------------------------------
##----------------------------------------------------
#           Requirements Installer & Updater
#                       by
#                     Stan44
#       Modify as needed if you have issues
#----------------------------------------------------
## Installs the required packages to run your program
#def install_or_update_requirements():
    #current_directory = os.path.dirname(os.path.abspath(__file__))
    #requirements_file = os.path.join(current_directory, 'requirements.txt')

   # print('Installing or updating requirements, please wait...')
    ## Install or update required packages from requirements.txt
  #  with open(requirements_file, 'r') as file:
 #       requirements = file.readlines()
#    requirements = [req.strip() for req in requirements]

#    for requirement in requirements:
#        try:
         #   result = subprocess.run(['pip', 'show', requirement], capture_output=True, text=True)
        #    if result.returncode == 0:
       #         print(f"Requirement '{requirement}' is already installed.")
      #      else:
     #           print(f"Requirement '{requirement}' is not installed.")
    #            subprocess.run(['pip', 'install', requirement], check=True)
   #     except Exception as e:
  #          print("An error occurred while checking or installing the package:", str(e))
 #           continue

#        try:
        #    result = subprocess.run(['pip', 'install', '--upgrade', requirement], capture_output=True, text=True)
       #     if result.returncode == 0:
      #          print(f"Requirement '{requirement}' is up to date.")
     #       else:
    #            print(f"An error occurred while updating the requirement '{requirement}'.")
   #     except Exception as e:
  #          print("An error occurred while checking or updating the package:", str(e))
 #           continue

#install_or_update_requirements()

#
