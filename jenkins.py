from errbot import BotPlugin, botcmd
from jenkins import Jenkins as JenkinsAPI
from jenkins import JenkinsError
import pprint

class Jenkins(BotPlugin): 
    def activate(self):
        if not self.config:
            # Don't allow activation until we are configured
            message = 'Jenkins plugin is not configured, please use {prefix}plugin config jenkins.'
            self.log.info(message)
            self.warn_admins(message)
        self.j = JenkinsAPI(self.config['JENKINS_URL'],
                            self.config['JENKINS_USERNAME'],
                            self.config['JENKINS_PASSWORD'])
        super().activate()
    
    def get_configuration_template(self):
        return {'JENKINS_URL': 'https://changeme',
                'JENKINS_USERNAME':'changeme',
                'JENKINS_PASSWORD':'changeme'}
    
    def callback_message(self, mess):
        if mess.body.find('cookie') != -1:
            self.send(
                mess.frm,
                "What what somebody said cookie!?",
            )

    @botcmd
    def deploy(self, mess, args):
        return u'For deploy syntax: {prefix}help deploy'

    @botcmd
    def deploy_list(self, mess, args):
        """ List existing targets """
        jobs = self.j.jobs
        yield pprint.pformat(jobs)
        # TODO: Do this list better

    @botcmd(split_args_with=None)
    def deploy_dev(self, mess, args):
        """ TESTING COMMAND """
        yield args[0]
        jobname = 'test-staging2'
        job = self.j.jobs[jobname]
        lgb = job.get_last_good_build()
        yield "last good build: " + str(lgb)
        yield "result url: " + lgb.get_result_url()
        yield pprint.pformat(lgb._data)

    @botcmd(split_args_with=None)
    def deploy_to(self, mess, args):
        """ Deploy to a target: {prefix}deploy to servername """
        # TODO: more validation of which job here
        target = args[0]
        if not target:
            return "Target must be specified. !deploy to servername"
        self.j.job_build('Deploy RAMS Instance - Fabric', {'SERVER': target})

    @botcmd(split_args_with=None)
    def deploy_target_add(self, mess, args):
        """ Add a new target for deploys """
        if len(args) < 2:
            return u'usage: !deploy target add <env> <friendly name> ' \
                '<server name> <channels to notify>'
        name = args[0]
        url = args[1] 
        self[name] = url
        return u'Event added to list.'
    
    @botcmd(split_args_with=None)
    def deploy_target_remove(self, mess, args):
        """ Remove a target for deploys """
        if len(args) < 1:
            return u'usage: !deploy target remove <name>'
        name = args[0]
        try:
            del self[name]
            return u'Target removed from list.'
        except KeyError:
            return u'That target is not in the list. ' \
                   'Use !deploy target list to see all targets.'
    @botcmd
    def deploy_target_list(self, mess, args):
        """ List all deploy targets """
        if len(self) > 0:
            return u'|Name|URL|\n|:---|:---|\n' + u'\n'.join(
                ['|{name}|{url}|'.format(
                    name=name,
                    url=self[name]
                ) for name in self])
        else:
            return u'No targets currently in list. ' \
                   'Use !deploy target add to define one.'