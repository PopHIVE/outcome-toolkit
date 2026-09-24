import {
  api2Project,
  APIProjectSpec,
  type ProjectID,
  type ProjectType,
  type UserID,
  type UserType,
} from "@/types";
import { API_PROJECT_INFO_URL } from "@/util/Consts";
import _ from "lodash";
import { defineStore } from "pinia";
import { EMPTY_USER, SAMPLE_PROJECT_1, SAMPLE_PROJECTS } from "./SAMPLE_PROJECTS";
import { okOrThrow } from "./fetching";

export type ProjectStoreState = {
  /** Data for all loaded projects.
   * For a HA user, this will (must) only ever be projects they have access to.
   * For an admin user, this will be all projects.
   */
  _projects: Record<ProjectID, ProjectType>;

  /**
   * The project currently being viewed.
   */
  _currentProject: ProjectID | null;

  /** Dictionary of members we know about (loaded lazily from server to reduce exposure on front end.) */
  _knownMembers: Record<UserID, UserType>;
};

export const useProjectStore = defineStore("outcome-toolkit-project", {
  state: () => {
    const state: ProjectStoreState = {
      // FIXME Remove sample data; project store should be empty before fetching.
      _currentProject: SAMPLE_PROJECT_1.id, // FIXME will be null,
      _projects: _.keyBy([...SAMPLE_PROJECTS /*, ...ACTUAL_PROJECTS*/], "id"), // {},
      _knownMembers: {}, //_.keyBy(SAMPLE_USERS, "id"), // {},
    };
    return state;
  },
  actions: {
    /** @return true Once data for the given (default: current) project has arrived over the network. Also returns false if there is no current project and the project ID is unspecified */
    dataIsReady(maybeID?: ProjectID) {
      const id = maybeID ?? this._currentProject;
      return id !== null && id in this._projects;
    },

    /**
     * Get the project info for the current project, or null
     * if there either is no current project, or the info is not yet available.
     */
    project(): ProjectType | null {
      return this._currentProject === null ? null : (this._projects[this._currentProject] ?? null);
    },

    /**
     * Set the current project to the given ID, fetching data from the server if necessary and possible.
     */
    setProject(id: ProjectID) {
      if (!(id in this._projects)) {
        this.fetchProjectData(id).then(() => (this._currentProject = id));
      } else {
        this._currentProject = id;
      }
    },

    /**
     * Fetches data from the server for the given project ID.
     */
    async fetchProjectData(id: ProjectID) {
      // For debug, use user from environment
      const prpEmail = import.meta.env.VITE_PRP_EMAIL ?? "";

      fetch(API_PROJECT_INFO_URL, {
        method: "POST",
        body: JSON.stringify({ project_id: id }),
        cache: "no-cache",
        headers: {
          "Content-Type": "application/json",
          "prp-email": prpEmail,
        },
      })
        .then(okOrThrow)
        .then((res) => res.json())
        .then(APIProjectSpec.check)
        .then((p) => {
          this._projects[p.id] = api2Project(p);
          for (const u of p.users) {
            // NOTE: Technically this may overwrite a user but it should just be overwritten with a newer version of that same user.
            this._knownMembers[u.id] = u;
          }
        })
        .catch((err) => {
          console.error("Couldn't load project details", err); // TODO remove output of "err" before shipment
          // TODO: Catch case where user is not authorized if this isn't caught by the reverse proxy.
        });
    },

    user(userID: UserID): UserType | undefined {
      return this._knownMembers[userID] ?? EMPTY_USER;
    },
  },
});
