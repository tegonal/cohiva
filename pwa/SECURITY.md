# How to do security updates?

0. Show dependency and installed version(s)

   yarn why -R <package>

1. Try to update direct dependency

   yarn up <direct dependency>

2. Check if package has been updated to the required version. If not, add it to `resolutions` in `package.json` and add it to the list below for later removal.

3. Install new resolutions with

   yarn install

# Dependency Resolutions (Yarn)

We use Yarn `resolutions` to patch transitive dependency vulnerabilities
when upstream packages have not yet released fixes.

## Removing overrides

Try to remove the packages from `resolutions` in `package.json`
when the parent packages have been updated. Remove packages one by
one and check after each package with `yarn install` if an older version
is installed or not. If an older (vulnerable) package is installed,
revert the change in the resolutions list, since it is still needed.
