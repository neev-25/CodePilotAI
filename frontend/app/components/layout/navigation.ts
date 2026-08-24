import {
    LayoutDashboard,
    FolderGit2,
    BarChart3,
    Search,
    ShieldCheck,
    FileCode2,
    GitPullRequest,
    TestTube2,
    Network,
    Settings,
    User,
} from "lucide-react";

export const navigation = [

    {
        title: "Dashboard",
        href: "/",
        icon: LayoutDashboard,
    },

    {
        title: "Repositories",
        href: "/repositories",
        icon: FolderGit2,
    },

    {
        title: "Analysis",
        href: "/analysis",
        icon: BarChart3,
    },

    {
        title: "Security",
        href: "/security",
        icon: ShieldCheck,
    },

    {
        title: "Search",
        href: "/search",
        icon: Search,
    },

    {
        title: "Documentation",
        href: "/documentation",
        icon: FileCode2,
    },

    {
        title: "Pull Requests",
        href: "/pull-request",
        icon: GitPullRequest,
    },

    {
        title: "Testing",
        href: "/testing",
        icon: TestTube2,
    },

    {
        title: "Architecture",
        href: "/architecture",
        icon: Network,
    },

    {
        title: "Settings",
        href: "/settings",
        icon: Settings,
    },

    {
        title: "Profile",
        href: "/profile",
        icon: User,
    },

];