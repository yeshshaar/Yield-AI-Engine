import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { MongoClient } from "mongodb";
import { StoredReport } from "./types";

const fileStorePath = path.join(process.cwd(), "data", "reports.json");
let mongoClient: MongoClient | null = null;

async function collection() {
  if (!process.env.MONGODB_URI) return null;
  mongoClient ??= new MongoClient(process.env.MONGODB_URI);
  await mongoClient.connect();
  return mongoClient.db(process.env.MONGODB_DB || "urdestiny").collection<StoredReport>("reports");
}

async function readFileStore() {
  try {
    const contents = await readFile(fileStorePath, "utf8");
    return JSON.parse(contents) as StoredReport[];
  } catch {
    return [];
  }
}

async function writeFileStore(reports: StoredReport[]) {
  await mkdir(path.dirname(fileStorePath), { recursive: true });
  await writeFile(fileStorePath, JSON.stringify(reports, null, 2), "utf8");
}

export async function saveReport(report: StoredReport) {
  const reports = await collection();
  if (reports) {
    await reports.insertOne(report);
    return;
  }

  const current = await readFileStore();
  current.push(report);
  await writeFileStore(current);
}

export async function getReport(id: string) {
  const reports = await collection();
  if (reports) {
    return reports.findOne({ id });
  }

  const current = await readFileStore();
  return current.find((report) => report.id === id) || null;
}

export async function unlockReport(id: string, paymentId: string) {
  const reports = await collection();
  if (reports) {
    await reports.updateOne({ id }, { $set: { unlocked: true, paymentId } });
    return getReport(id);
  }

  const current = await readFileStore();
  const index = current.findIndex((report) => report.id === id);
  if (index === -1) return null;
  current[index] = { ...current[index], unlocked: true, paymentId };
  await writeFileStore(current);
  return current[index];
}
