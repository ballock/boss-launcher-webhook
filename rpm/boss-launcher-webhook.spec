%define svdir %{_sysconfdir}/supervisor/conf.d/

Name: boss-launcher-webhook
Version: 0.2.0
Release: 1

Group: Applications/Engineering
License: GPLv2+
URL: https://github.com/MeeGoIntegration/boss-launcher-webhook
Source: %{name}-%{version}.tar.gz

BuildArch: noarch

BuildRequires: python3-setuptools
BuildRequires: python3-rpm-macros

Requires(post): boss-standard-workflow-common
Requires(post): python3-boss-skynet >= 0.6.6
Requires: python3-Django
Requires: python3-boss-common >= 0.27.10
Requires: python3-djangorestframework
Requires: python3-requests
Requires: python3-xml
Requires: python3-django-filter
Requires: python3-mysqlclient
Requires: uwsgi-python3
Recommends: boss-participant-create_project
Recommends: boss-participant-auto_promote

Summary: VCS webhook handler

%description
Webhook handler for gitlab, github and bitbucket that receives data as a POST callback and launches a ruote process

%package -n obs-service-tar-git
Requires: git
Requires: obs-source_service
Summary: OBS source service to generate sources from git
%description -n obs-service-tar-git
This package provides the service to generate source from git inside an OBS source service

%package -n obs-service-webhook
Requires: obs-source_service
Requires: python3-argparse
Requires: python3-requests
Summary: OBS source service to manage webhooks
%description -n obs-service-webhook
This package provides the service to update webhooks from OBS. It ensures that only users who have access to a package can update the webhook for that package.

%package -n boss-participant-trigger_service
Requires(post): boss-standard-workflow-common
Requires(post): python3-boss-skynet >= 0.6.6
Requires: osc3
Requires: python3-boss-common >= 0.27.10
Requires: python3-lxml
Requires: python3-pyaml
Summary: BOSS participant to handle webhooks
%description -n boss-participant-trigger_service
This package provides the participant that handles creating and/or triggering  _service files in OBS, in response to webhook triggers

%package -n boss-participant-create_project
Requires(post): boss-standard-workflow-common
Requires(post): python3-boss-skynet >= 0.6.6
Requires: boss-launcher-webhook
Requires: osc3
Requires: python3-boss-common >= 0.27.10
Requires: python3-lxml
Summary: BOSS participant to handle webhooks
%description -n boss-participant-create_project
This package provides the participant that handles creating project files in OBS, in response to webhook triggers
It must run on the webhook server as it accesses the database.

%package -n boss-participant-get_src_state
Requires(post): boss-standard-workflow-common
Requires(post): python3-boss-skynet >= 0.6.6
Requires: python3-boss-common >= 0.27.10
Summary: BOSS participant to handle webhooks
%description -n boss-participant-get_src_state
This package provides the participant that checks that there is src is ready to build in OBS projects. Usually this means the service has succeeded.

%package -n boss-participant-auto_promote
Requires(post): boss-standard-workflow-common
Requires(post): python3-boss-skynet >= 0.6.6
Requires: boss-launcher-webhook
Requires: python3-boss-common >= 0.27.10
Summary: BOSS participant to handle webhooks
%description -n boss-participant-auto_promote
This package provides the participant that handles promotion of gated projects, in response to webhook triggers
It must run on the webhook server as it accesses the database.

%prep
%setup -q %{name}-%{version}

%build
%python3_build

%install
%python3_install
make PREFIX=%{_prefix} DESTDIR=%{buildroot} install


%post
if [ $1 -ge 1 ]; then
    skynet apply || true
    skynet reload delete_webhook || true
    skynet reload handle_webhook || true
    skynet reload relay_webhook || true
    skynet register --all || true
fi

%post -n boss-participant-create_project
if [ $1 -ge 1 ]; then
    skynet apply || true
    skynet reload create_project || true
    skynet register --all || true
fi

%post -n boss-participant-get_src_state
if [ $1 -ge 1 ]; then
    skynet apply || true
    skynet reload get_src_state || true
    skynet register --all || true
fi

%post -n boss-participant-trigger_service
if [ $1 -ge 1 ]; then
    skynet apply || true
    skynet reload trigger_service || true
    skynet register --all || true
fi

%post -n boss-participant-auto_promote
if [ $1 -ge 1 ]; then
    skynet apply || true
    skynet reload auto_promote || true
    skynet register --all || true
fi

%files
%defattr(-,root,root,-)
%doc example/apache_webhook.conf
%doc README
%config(noreplace) %{_sysconfdir}/skynet/webhook.conf
%config(noreplace) %{svdir}/delete_webhook.conf
%config(noreplace) %{svdir}/handle_webhook.conf
%config(noreplace) %{svdir}/relay_webhook.conf
%{python3_sitelib}/webhook_launcher
%{python3_sitelib}/*egg-info
%{_datadir}/webhook_launcher
%{_datadir}/boss-skynet/delete_webhook.py*
%{_datadir}/boss-skynet/handle_webhook.py*
%{_datadir}/boss-skynet/relay_webhook.py*

%files -n boss-participant-auto_promote
%defattr(-,root,root,-)
%config(noreplace) %{svdir}/auto_promote.conf
%{_datadir}/boss-skynet/auto_promote.py*

%files -n boss-participant-create_project
%defattr(-,root,root,-)
%config(noreplace) %{svdir}/create_project.conf
%{_datadir}/boss-skynet/create_project.py*

%files -n boss-participant-get_src_state
%defattr(-,root,root,-)
%config(noreplace) %{svdir}/get_src_state.conf
%{_datadir}/boss-skynet/get_src_state.py*

%files -n boss-participant-trigger_service
%defattr(-,root,root,-)
%config(noreplace) %{svdir}/trigger_service.conf
%{_datadir}/boss-skynet/trigger_service.py*

%files -n obs-service-tar-git
%defattr(-,root,root,-)
%dir /usr/lib/obs
%dir /usr/lib/obs/service
/usr/lib/obs/service/tar_git
/usr/lib/obs/service/tar_git.service

%files -n obs-service-webhook
%defattr(-,root,root,-)
%dir /usr/lib/obs
%dir /usr/lib/obs/service
/usr/lib/obs/service/webhook
/usr/lib/obs/service/webhook.service
