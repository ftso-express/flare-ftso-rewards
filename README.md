# flare-ftso-rewards
Claiming Rewards from Being an FTSO


# Build

`docker build -t dulee/claim_ftso_rewards:latest -t dulee/claim_ftso_rewards:latest .`

# Run

## Run (Flare)

`docker run --rm -t -v $(pwd)/config.yml:/app/config.yml -v $(pwd)/logs:/app/logs dulee/claim_ftso_rewards:latest -n flare`

*Verbose*
`docker run --rm -t -v $(pwd)/config.yml:/app/config.yml -v $(pwd)/logs:/app/logs dulee/claim_ftso_rewards:latest -n flare -v`

## Run (Sonbird)

`docker run --rm -t -v $(pwd)/config.yml:/app/config.yml -v $(pwd)/logs:/app/logs dulee/claim_ftso_rewards:latest -n songbird`

*Verbose*
`docker run --rm -t -v $(pwd)/config.yml:/app/config.yml -v $(pwd)/logs:/app/logs dulee/claim_ftso_rewards:latest -n songbird -v`

## Claim (Flare)

`docker run --rm -t -v $(pwd)/config.yml:/app/config.yml -v $(pwd)/logs:/app/logs dulee/claim_ftso_rewards:latest -n flare -c`

## Claim (Sonbird)

`docker run --rm -t -v $(pwd)/config.yml:/app/config.yml -v $(pwd)/logs:/app/logs dulee/claim_ftso_rewards:latest -n songbird -c`
