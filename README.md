# BetterEAMS

<p align="center">
  <img src="https://github.com/user-attachments/assets/9333471a-e17a-41db-93d0-fd22c1502358" width="650" />
</p>


BetterEAMS is a Tampermonkey userscript that replaces ShanghaiTech EAMS course election pages with a cleaner course workspace, schedule view, filtering tools, plan-gap hints, favorites, and EAMS-backed select/drop actions.

## Install

Install or update from:

https://raw.githubusercontent.com/Maotechh/BetterEAMS/main/userscripts/bettereams.user.js

Tampermonkey will use the script metadata in `userscripts/bettereams.user.js` to check GitHub for future updates:

- `@updateURL`: metadata/version checks
- `@downloadURL`: updated script download

## Scope

The script only runs on EAMS course election entry pages:

- `stdElectCourse!defaultPage.action`
- `stdElectCourse.action`

It intentionally does not inject into syllabus/detail pages.
