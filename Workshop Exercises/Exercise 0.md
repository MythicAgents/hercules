## Exercise 0 - Install Mythic

### mythic.lab
This sequence of events happens on the Linux `mythic.lab` host.

#### Install Mythic (done for you)
Mythic is currently only supported to run on intel-based Linux machines. On the `mythic.lab` machine run the following:

1. `git clone https://github.com/its-a-feature/Mythic`
2. `cd Mythic`

#### Configure Mythic
Mythic supports many configuration options, but for now we'll just pre-set our administrator password. When Mythic starts for the first time, the `MYTHIC_ADMIN_USER` and `MYTHIC_ADMIN_PASSWORD` are used to create the initial user. After the first start though, these two values are not used.

3. `sudo ./mythic-cli config set MYTHIC_ADMIN_USER mythic_admin`
4. `sudo ./mythic-cli config set MYTHIC_ADMIN_PASSWORD mythic_password`

Services that need passwords but don't have them set automatically will generate passwords on first launch. This includes things like `RabbitMQ`, `PostgreSQL`, and the admin account. Normally, you shouldn't pre-configure these; however, for the lab to make things easier, we'll pre-configure the `RabbitMQ` password so we don't need to update configs along the way for the labs:

5. `sudo ./mythic-cli config set RABBITMQ_PASSWORD WrSJkwAa5yexxytHQH580j3Rlb4Nrc`

We'll want to start with everything fresh, so we'll clear out any existing `RabbitMQ` and `PostgreSQL` information:

6. `sudo ./mythic-cli database reset`
7. `sudo ./mythic-cli rabbitmq reset`
8. `sudo ./mythic-cli config set REBUILD_ON_START false`

#### Install C2 Profiles
We will be creating our own Mythic Agent for this workshop (and eventually our own C2 Profile), but for now we'll install the `http` public C2 profile as a starting point:

9. `sudo ./mythic-cli install github https://github.com/MythicC2Profiles/http`

#### Start Mythic

10. `sudo ./mythic-cli start`

#### Log in

Open up a browser on your `dev-desktop.lab` Windows box and go to `https://mythic.lab:7443` and log in with `mythic_admin` and password `mythic_password`. 