using CsvHelper.Configuration;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace NLP
{
    public sealed class AccidentRecordMap : ClassMap<AccidentRecord>
    {
        public AccidentRecordMap()
        {
            Map(m => m.PublicationDate).Name("Publication Date");
            Map(m => m.UpdateDate).Name("Update Date");
            Map(m => m.MetaLocation).Name("Meta Location");
            Map(m => m.Title).Name("Title");
            Map(m => m.HtmlText).Name("HTML Text");
            Map(m => m.RawText).Name("Raw Text");
        }
    }

}