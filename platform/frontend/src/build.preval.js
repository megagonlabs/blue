import git from "git-rev-sync";
import preval from "next-plugin-preval";
async function getBuildInfo() {
    return {
        short: git.short(),
        long: git.long(),
        branch: git.branch(),
    };
}
export default preval(getBuildInfo());
