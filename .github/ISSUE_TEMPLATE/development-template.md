---
name: Development Template
about: Follow these steps to implement a new feature, commit your work, and open a
  pull request following best practices.
title: ''
labels: ''
assignees: ''

---

## Development Steps

0. Make Sure you are on the repo dir.
```bash
cd ~/frappe-bench/apps/auth_hub
```

1. Checkout the `develop` branch
```bash
git checkout develop
git pull origin develop
````

2. Create a new branch using [**Conventional Commits**](https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13).

```bash
git checkout -b feat/<short-description>
```


3. Implement the feature or fix
* Write clean, focused code
* Follow existing project conventions


4. Commit changes using Conventional Commits

```bash
git commit -m "feat: add automatic price adjustment"
```

5. Push the branch

```bash
git push origin feat/<short-description>
```

6. Open a Pull Request
* Base branch: `develop`
* Clear title & description
