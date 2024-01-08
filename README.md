# dynamic-airflow-dag-task

## command to handle error in cloudshell

* git clone from github repo with access token, [link](https://stackoverflow.com/questions/42148841/github-clone-with-oauth-access-token):
```
git clone https://username:token@github.com/username/repo.git
```

* push to gitlab repo with access token, [link](https://stackoverflow.com/questions/42074414/gitlab-push-to-a-repository-using-access-token):
```
git push https://gitlab-ci-token:<access_token>@gitlab.com/myuser/myrepo.git <branch_name>
```

* fix error `NoPermission (FileSystemError)`, [link](https://stackoverflow.com/questions/66496890/vs-code-nopermissions-filesystemerror-error-eacces-permission-denied):
```
sudo chown -R username path 
```

* run docker compose
```
docker compose up
``` 

* list docker container
```
docker container ps -a
```

* delete DAG
```
docker exect -it <container_id> airflow dags delete <dag_name>
```
