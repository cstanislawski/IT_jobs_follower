# IT job offers follower

## Supported job portals

NoFluffJobs - [source code](job_portals/nfj.py)

JustJoinIT - [source code](job_portals/jjt.py)

### Jobs portals planned to support

- BulldogJob,
- SolidJobs

### How to use

1. Clone the repository,
2. Add label and url with filters to data_sources in [config.yaml](config.yaml),
3. Run the script,
4. See the results in [job_offers.yaml](offers/job_offers.yaml)

### TO DO

- Support job portals:
  - SolidJobs
  - BulldogJob
- Merge offers on different portals together based on the label
- [JJI-only] If offer is for multiple cities liList salary & sort by it in job_offers.yamlnk the main offer with cities listed
- Provide link to company's glassdoor / other sites
- Show difference in offers between days (what offers added, what removed):
  - what offers were added, what were removed,
  - differences in particular offer (increased salary, additional benefits etc)
- Generate HTML summary based on the info
- Find duplicate offers on other websites (select best ones if they differ?)
- Contributing.md (if one appears)
- ~~List salary & sort by it in [job_offers.yaml](offers/job_offers.yaml)~~ - done 07.03.2023
- ~~List days in order of newest -> oldest~~ - done 03.02.2023
- ~~JustJoinIT - full support for remote offers~~ - done 26.02.2023
- ~~NoFluffJobs - full support for all offers~~ - done 25.02.2023
