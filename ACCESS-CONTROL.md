# access control

### Roles
#### Administrator
- `Read` `Write` operations in agent registry for any agent
- `Read` `Write` operations in data registry for any data
- administrator tools
  - deploy and stop agents
  - update user roles
- development tools
  - form designer
- `Read` `Write` any sessions
#### Member
- `Read` operations in agent registry for any agent
- `Read` operations in data registry for any data
- `Read` `Write` any sessions that they own / participate
  - add and modify agent properties for sessions only
#### Developer
- `Read` operations in agent registry for any agent
- `Read` operations in data registry for any data
- `Write` operations in agent / data registries for any agent / data they created
  - deploy and stop agents
- development tools
  - form designer
- `Read` `Write` any sessions that they own / participate
  - add and modify agent properties for sessions only
#### Guest
- `Read` operations in agent registry for any agent
- `Read` operations in data registry for any data
- `Read` any sessions that they participate

To update role, go to "Users" under "Admin. Tools" menu (you need to be an administrator to do that.)
### Notes 
- Participants are members of a session; you can add members under "session details" dialog.
- Session is owned by the user who created it; ownership it's not transferable.
- `Write` operations includes `CREATE`, `UPDATE`, and `DELETE`.
- Role permissions are not configurable through UI: update `model.conf` and `policy.csv` (based on [casbin](https://github.com/casbin/pycasbin)), then restart the API service.
