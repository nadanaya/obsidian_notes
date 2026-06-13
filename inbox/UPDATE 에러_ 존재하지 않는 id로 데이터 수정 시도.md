To resolve GitHub file size limit issues due to large commit histories, `git filter-repo` can be used to remove unnecessary files and directories from the commit history. Here's a step-by-step guide:

**Removing Unnecessary Files**

1. Install `git-filter-repo`: `pip install git-filter-repo`
2. Run `git filter-repo --path dental_app/build/ --invert-paths --force` to remove the build folder from the commit history.

**Updating the Remote Repository**

3. Update the remote repository: `git remote add origin https://github.com/2026-capstone-design/dentalink_app.git`
4. Force-push the changes: `git push origin HEAD --force`

By following these steps, developers can effectively manage their codebase and resolve file size limit issues.

#evolved