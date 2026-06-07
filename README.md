# BetterEAMS

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

## Repository

This repository contains only the BetterEAMS userscript and minimal project metadata. The previous standalone course analytics page, crawler scripts, and generated datasets have been removed.
