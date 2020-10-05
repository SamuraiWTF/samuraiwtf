# Amazon Linux Notes
There is a Ansible playbook available for Amazon Linux (i.e. to set up SamuraiWTF in a AWS Workspaces).
This is for online classrooms.  There are some caveats to this build:

  * You must start with a Amazon Linux workspace.  4GB Ram is sufficient.  Disk size can be 20GB or more.
  * The build sets up targets and tools but some customizations, such as desktop wallpaper, must be completed manually.
  * AWS terms of services does not allow any hacking / scanning from workspaces. Therefore it is recommended that you remove the default outbound rule for the workspaces Security Group, so that no traffic will be able to leave the workspace.  Strictly speaking, once SamuraiWTF is installed and configured, internet access outbound should no longer be needed.  All the target apps are contained within the environment as local destinations.

## Amazon Linux Installation
  * Create a Workspace (4+GB Ram, 20+ GB user disk space)
  * Log in, open a terminal, and run each of the the commands under [install/amazon-linux/aws_workspace_bootstrap.sh](https://raw.githubusercontent.com/SamuraiWTF/samuraiwtf/amazon-linux/install/amazon-linux/aws_workspace_bootstrap.sh) in this branch.
  * Type your workspace password when prompted for your *BECOME Password*.  This is what the Ansible playbook uses for sudo.