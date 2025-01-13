import { redirect } from "next/navigation";


//const baseurl = '.preprod.aws.chatbees.ai'
const baseurl =
  process.env.NEXT_PUBLIC_CHATBEES_BASEURL ?? ".us-west-2.aws.chatbees.ai";

export function getServiceUrl(aid: string): string {
  if (baseurl == "localhost") {
    return "http://localhost:8080";
  }
  return "https://" + aid + baseurl;
}

export function getHeaders(
  aid: string,
  apiKey: string,
  upload: boolean = false,
): { [key: string]: string } {
  let headers: { [key: string]: string } = {
    "Content-Type": "application/json",
    "api-key": apiKey,
  };
  if (baseurl == "localhost" || window.location.origin.includes("localhost")) {
    headers["x-org-url"] = aid;
  }

  if (upload) {
    delete headers["Content-Type"];
  }
  return headers;
}

function redirectToLogin(
  reason: string = "Session expired, please sign-in again",
) {
  const reasonStr = reason == "" ? "" : `?why=${reason}`;
  if (typeof window !== "undefined") {
    // Client redirect
    window.location.href = `/auth/signin${reasonStr}`;
  } else {
    // Server redirect
    redirect(`/auth/signin${reasonStr}`);
  }
}

async function fetch_url<T = any>(
  aid: string,
  shortliveApiKey: string,
  url_suffix: string,
  body: BodyInit,
): Promise<T> {
  if (aid == "") {
    throw new Error("Account ID not found", { cause: 404 });
  }

  const url: string = getServiceUrl(aid) + url_suffix;

  return await do_fetch_url<T>(aid, shortliveApiKey, url, body);
}

async function do_fetch_url<T = any>(
  aid: string,
  shortliveApiKey: string,
  url: string,
  body: BodyInit,
): Promise<T | any> {
  const headers: HeadersInit = getHeaders(aid, shortliveApiKey);

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: headers,
      body: body,
    });

    if (response.ok) {
      return await response.json();
    } else if (response.status != 401) {
      throw new Error(
        `status: ${response.status}, error: ${response.statusText}`,
        { cause: response.status },
      );
    }

    // 401 errors bypass error check. We'll redirect users to login page
  } catch (error) {
    console.log("Caught error ", error);
    throw error;
  }

  // If try/catch block did not return or throw, redirect to login (we got 401)
  redirectToLogin();
}

// Function to process errors
export function processError(
  error: Error,
  prefix: string,
  redirect_href: string = "",
): void {
  // Handle 401s first
  if (error.message.startsWith("status: 401") || error.cause == 401) {
    redirectToLogin();
  }

  console.error(`${prefix} error: ${error.message}`);
  if (typeof window !== "undefined") {
    //window.alert(`${prefix} error: ${error.message}`);
    if (redirect_href !== "") {
      console.log("redirect_href", redirect_href);
      window.location.href = redirect_href;
    }
  }
  // Non-browser env. TODO how to return error? or redirect?
}


// Collection related APIs

export type Collection = { 
  name: string;
  description?: string;
  publicRead?: boolean;
  persona?: string;
  negativeResponse?: string;
};

export interface CollectionDescription {
  collection: Collection;
};

export async function CreateChatBeesCollection(
  aid: string,
  apiKey: string,
  collectionName: string,
): Promise<any> {
  const url_suffix = "/collections/create";
  const json_body = JSON.stringify({
    collection_name: collectionName,
    namespace_name: "public",
    public_read: false,
  });

  return await fetch_url(aid, apiKey, url_suffix, json_body);
}

export async function DeleteCollection(
  aid: string,
  apiKey: string,
  collectionName: string,
): Promise<any> {
  const url_suffix = "/collections/delete";
  const json_body = JSON.stringify({
    collection_name: collectionName,
    namespace_name: "public",
  });

  return await fetch_url(aid, apiKey, url_suffix, json_body);
}

export async function ListCollections(
  aid: string,
  apiKey: string,
): Promise<{ collections: Collection[] }> {
  const url_suffix = "/collections/list";
  const json_body = JSON.stringify({ namespace_name: "public" });

  const data = await fetch_url(aid, apiKey, url_suffix, json_body);
  if (data == null) {
    return { collections: [] };
  }
  let collections: Collection[] = [];
  for (let colName of data["names"]) {
    collections.push({ name: colName });
  }

  return { collections: collections };
}

export async function DescribeCollection(
  aid: string,
  apiKey: string,
  collectionName: string,
): Promise<CollectionDescription> {
  const url_suffix = "/collections/describe";
  const json_body = JSON.stringify({
    namespace_name: "public",
    collection_name: collectionName,
  });

  const data = await fetch_url(aid, apiKey, url_suffix, json_body);
  /**
   * {
   *     "description": null,
   *     "chat_attributes": null,
   *     "public_read": null,
   * }
   **/

  let persona: string = "You are an AI assistant.";
  let negativeResponse: string = "I'm sorry, I don't have relevant information to answer your question. If you have any other question, feel free to ask!";
  if (data["chat_attributes"] != null) {
    if (data["chat_attributes"]["persona"] != null) {
      persona = data["chat_attributes"]["persona"];
    }
    if (data["chat_attributes"]["negative_response"] != null) {
      negativeResponse = data["chat_attributes"]["negative_response"];
    }
  }

  return {
    collection: {
      name: collectionName,
      description: data["description"] ?? "",
      publicRead: data["public_read"] ?? false,
      persona: persona,
      negativeResponse: negativeResponse,
    },
  };
}

export async function ConfigureChat(
  aid: string,
  apiKey: string,
  collectionName: string,
  persona: string | null,
  negativeResponse: string | null,
): Promise<any> {
  const url_suffix = "/docs/configure_chat";
  const json_body = JSON.stringify({
    namespace_name: "public",
    collection_name: collectionName,
    chat_attributes: {
      persona: persona,
      negative_response: negativeResponse,
    },
  });

  return await fetch_url(aid, apiKey, url_suffix, json_body);
}

export async function ShareOrUnshareCollection(
  aid: string,
  apiKey: string,
  collectionName: string,
  publicRead: boolean,
): Promise<any> {
  const url_suffix = "/collections/configure";
  const json_body = JSON.stringify({
    namespace_name: "public",
    collection_name: collectionName,
    public_read: publicRead,
  });

  return await fetch_url(aid, apiKey, url_suffix, json_body);
}


// Document related APIs

export async function DeleteDocument(
  aid: string,
  apiKey: string,
  collectionName: string,
  fileName: string,
): Promise<any> {
  const url_suffix = "/docs/delete";
  const json_body = JSON.stringify({
    namespace_name: "public",
    collection_name: collectionName,
    doc_name: fileName,
  });

  return await fetch_url(aid, apiKey, url_suffix, json_body);
}

export async function ListDocFiles(
  aid: string,
  apiKey: string,
  collectionName: string,
): Promise<{ docs: string[] }> {
  const url_suffix = "/docs/list";
  const json_body = JSON.stringify({
    namespace_name: "public",
    collection_name: collectionName,
  });

  const data = await fetch_url(aid, apiKey, url_suffix, json_body);
  if (data == null) {
    return { docs: [] };
  }

  let docs: Document[] = [];
  for (let doc of data["documents"]) {
    docs.push(doc["name"]);
  }

  return { docs: docs };
}

export type AnswerRefs = {
  docName: string;
  pageNum: number;
  sampleText: string;
};

export async function Ask(
  aid: string,
  apiKey: string,
  collectionName: string,
  question: string,
  historyMessages: string[][],
  conversation_id: string | null,
): Promise<{
  answer: string;
  refs: AnswerRefs[];
  conversation_id: string;
  request_id: string;
}> {
  const url_suffix = "/docs/ask";
  const json_body =
    historyMessages.length == 0
      ? JSON.stringify({
          collection_name: collectionName,
          namespace_name: "public",
          question: question,
          conversation_id: conversation_id,
        })
      : JSON.stringify({
          collection_name: collectionName,
          namespace_name: "public",
          question: question,
          history_messages: historyMessages,
          conversation_id: conversation_id,
        });

  const respData = await fetch_url(aid, apiKey, url_suffix, json_body);
  const answer = respData["answer"];
  let refs: AnswerRefs[] = [];

  for (let ref of respData["refs"]) {
    refs.push({
      docName: ref["doc_name"],
      pageNum: ref["page_num"],
      sampleText: ref["sample_text"],
    });
  }

  return {
    answer: answer,
    refs: refs,
    conversation_id: respData["conversation_id"],
    request_id: respData["request_id"],
  };
}


// APIKey related APIs

export type ApiKey = {
  name: string;
  value: string;
};

export async function CreateChatBeesApiKey(
  aid: string,
  apiKey: string,
  apiKeyName: string,
): Promise<any> {
  const url_suffix = "/apikey/create";
  const json_body = JSON.stringify({ name: apiKeyName });

  return await fetch_url(aid, apiKey, url_suffix, json_body);
}

export async function DeleteChatBeesApiKey(
  aid: string,
  apiKey: string,
  apiKeyName: string,
): Promise<any> {
  const url_suffix = "/apikey/delete";
  const json_body = JSON.stringify({ name: apiKeyName });

  return await fetch_url(aid, apiKey, url_suffix, json_body);
}

export async function ListApiKeys(
  aid: string,
  apiKey: string,
): Promise<{ apiKeys: ApiKey[] }> {
  const url_suffix = "/apikey/list";
  const json_body = JSON.stringify({});

  const data = await fetch_url(aid, apiKey, url_suffix, json_body);

  let apiKeys: ApiKey[] = [];
  for (let apikey of data["api_keys"]) {
    apiKeys.push({ name: apikey["name"], value: apikey["masked_api_key"] });
  }

  return { apiKeys: apiKeys };
}


// Application related APIs

export enum ApplicationType {
  COLLECTION = "COLLECTION", // RAG chat
  GPT = "GPT", // directly talk to model
}

export interface CollectionTarget {
  namespace_name: string;
  collection_name: string;
}

export interface GPTTarget {
  provider: string;
  model: string;
}

export interface Application {
  application_name: string;
  application_type: ApplicationType;

  // Application target could be one of the supported targets.
  application_target: CollectionTarget | GPTTarget;
}

export async function CreateApplication(
  aid: string,
  apiKey: string,
  application: Application,
): Promise<any> {
  const url_suffix = "/applications/create";
  const json_body = JSON.stringify({ application: application });

  return await fetch_url(aid, apiKey, url_suffix, json_body);
}

export async function DeleteApplication(
  aid: string,
  apiKey: string,
  applicationName: string,
): Promise<any> {
  const url_suffix = "/applications/delete";
  const json_body = JSON.stringify({ application_name: applicationName });

  return await fetch_url(aid, apiKey, url_suffix, json_body);
}

export async function ListApplications(
  aid: string,
  apiKey: string,
): Promise<{ applications: Application[] }> {
  const url_suffix = "/applications/list";
  const json_body = JSON.stringify({});

  const data = await fetch_url(aid, apiKey, url_suffix, json_body);
  return data;
}


export function ValidateName(input: string): boolean {
  // Regular expression pattern to match the criteria
  const pattern = /^[a-zA-Z_][a-zA-Z0-9_-]{0,254}$/;

  // Check if the input matches the pattern
  return pattern.test(input);
}

export function ValidateEmail(input: string): boolean {
  // Regular expression pattern to match the criteria
  const pattern = /^.+@.+\..+$/;

  // Check if the input matches the pattern
  return pattern.test(input);
}
