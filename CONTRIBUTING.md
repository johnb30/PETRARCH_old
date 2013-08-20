# Contributing Code

You can check out the latest version of `petrarch` by cloning this repository using [git]().

	git clone https://github.com/eventdata/PETRARCH.git

To contribute to petrarch you should fork the repository, create a branch, add to or edit code, push your new branch to your fork of petrarch on GitHub, and then issue a pull request. See the example below.

	git clone https://github.com/YOUR_USERNAME/PETRARCH.git
	git checkout -b my_feature
	git add... # stage the files you modified or added
	git commit... # commit the modified or added files
	git push origin my_feature

Note that `origin` (if you are cloning the forked petrarch repository to your local machine) refers to that fork on GitHub, *not* the original (upstream) repository [https://github.com/eventdata/PETRARCH.git](https://github.com/eventdata/PETRARCH.git). If the upstream repository has changed since you forked and cloned it you can set an upstream remote:

	git remote add upstream https://github.com/eventdata/PETRARCH.git

You can then pull changes from the upstream repository and rebasing against the desired branch (in this example, master).

	git fetch upstream
	git rebase upstream/master

More detailed information on the use of git can be found in the [git documentation](http://git-scm.com/documentation).

# Coding Guidelines

The following are some guidelines on how new code should be written. Of course, there are special cases and there will be exceptions to these rules. However, following these rules when submitting new code makes the review easier so new code can be integrated in less time.

Uniformly formatted code makes it easier to share code ownership. The petrarch project tries to closely follow the official Python guidelines detailed in [PEP8](http://www.python.org/dev/peps/pep-0008/) that detail how code should be formatted and indented. Please read it and follow it.

In addition, we add the following guidelines:

 - Use underscores to separate words in non-class names: n_samples rather than nsamples.
 - Avoid multiple statements on one line. Prefer a line return after a control flow statement (if/for).
 - Use relative imports for references inside petrarch.
 - Please don’t use `import *`. It is considered harmful by the official Python recommendations. It makes the code harder to read as the origin of symbols is no longer explicitly referenced, but most important, it prevents using a static analysis tool like pyflakes to automatically find bugs in petrarch.
Use the numpy docstring standard in all your docstrings.
